from flask import Flask, jsonify, render_template, request, Response
import serial
import serial.tools.list_ports
import threading
import time
from datetime import datetime
import sqlite3
import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

app = Flask(__name__)
DB_FILE = os.path.abspath("sensor_data.db")
db_lock = threading.Lock()

arduino = None
arduino_lock = threading.Lock()
serial_thread_running = False

# ------------------ Database Init ------------------

def init_db():
    with db_lock:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                soil INTEGER,
                rain INTEGER,
                temperature REAL,
                humidity REAL,
                pump TEXT
            )
        """)
        conn.commit()
        conn.close()
        print("Database ready")

# ------------------ Insert ------------------

def insert_reading(timestamp, soil, rain, temperature, humidity, pump):
    with db_lock:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute("""
            INSERT INTO readings (timestamp, soil, rain, temperature, humidity, pump)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, soil, rain, temperature, humidity, pump))
        conn.commit()
        conn.close()

# ------------------ Latest ------------------

def get_latest_reading():
    with db_lock:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute("""
            SELECT soil, rain, temperature, humidity, pump
            FROM readings ORDER BY id DESC LIMIT 1
        """)
        row = c.fetchone()
        conn.close()

    if not row:
        return None

    return {
        "soil": row[0],
        "rain": "Yes" if row[1] == 1 else "No",
        "temperature": row[2],
        "humidity": row[3],
        "pump": row[4]
    }

# ------------------ History ------------------

def get_history_readings(limit=30):
    with db_lock:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute("""
            SELECT id, timestamp, soil, rain, temperature, humidity, pump
            FROM readings ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = c.fetchall()
        conn.close()

    history = []
    for r in reversed(rows):
        history.append({
            "id": r[0],
            "timestamp": r[1],
            "soil": r[2],
            "rain": "Yes" if r[3] == 1 else "No",
            "temperature": r[4],
            "humidity": r[5],
            "pump": r[6]
        })
    return history

# ------------------ Serial ------------------

def read_serial():
    global arduino, serial_thread_running
    buffer = ""

    while serial_thread_running:
        with arduino_lock:
            current_arduino = arduino

        if not current_arduino:
            time.sleep(1)
            continue

        try:
            line = current_arduino.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                time.sleep(0.1)
                continue

            buffer += " " + line

            if "Soil:" in buffer and "Hum:" in buffer and "Pump" in buffer:
                try:
                    soil = int(re.search(r"Soil:(\d+)", buffer).group(1))

                    rain_text = re.search(r"Rain:(Yes|No)", buffer).group(1)
                    rain = 1 if rain_text == "Yes" else 0

                    temp = float(re.search(r"Temp:([\d.]+)", buffer).group(1))
                    hum = float(re.search(r"Hum:([\d.]+)", buffer).group(1))

                    pump = "ON" if "Pump ON" in buffer else "OFF"

                    insert_reading(
                        datetime.now().isoformat(),
                        soil, rain, temp, hum, pump
                    )
                    print("Inserted:", soil, rain, temp, hum, pump)
                except Exception as e:
                    print("Parse error:", e)

                buffer = ""

        except Exception as e:
            print("Serial error:", e)
            with arduino_lock:
                arduino = None
            buffer = ""
            time.sleep(1)

        time.sleep(0.1)

# ------------------ Routes ------------------

DEFAULT_LATEST = {
    "soil": "--",
    "rain": "--",
    "temperature": None,
    "humidity": None,
    "pump": "--"
}

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/docs")
def docs():
    return render_template("docs.html")

@app.route("/data")
def data():
    reading = get_latest_reading() or DEFAULT_LATEST
    with arduino_lock:
        is_connected = arduino is not None
    reading["connected"] = is_connected
    return jsonify(reading)

@app.route("/history")
def history():
    return jsonify(get_history_readings())

@app.route("/ports")
def list_ports():
    ports = serial.tools.list_ports.comports()
    return jsonify([p.device for p in ports])

@app.route("/connect", methods=["POST"])
def connect_port():
    global arduino
    data = request.json
    port = data.get("port")
    
    with arduino_lock:
        if arduino:
            arduino.close()
            arduino = None
            
        if port:
            try:
                # Set a non-blocking timeout temporarily to test connection without freezing forever
                test_conn = serial.Serial(port, 9600, timeout=1)
                arduino = test_conn
                return jsonify({"status": "connected", "port": port})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 400
                
    return jsonify({"status": "disconnected"})

@app.route("/export")
def export_csv():
    with db_lock:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute("""
            SELECT timestamp, soil, rain, temperature, humidity, pump
            FROM readings ORDER BY id DESC LIMIT 1000
        """)
        rows = c.fetchall()
        conn.close()
        
    def generate():
        yield "Timestamp,Soil,Rain(1/0),Temperature,Humidity,Pump\n"
        for r in rows:
            yield f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]}\n"
            
    return Response(generate(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=history.csv"})

@app.route("/api/insights", methods=["POST"])
def get_insights():
    data = request.json or {}
    crop_type = data.get("crop", "General plants")
    
    recent = get_history_readings(10)
    if not recent:
        return jsonify({"suggestion": "Not enough data available yet to provide an insight."})
        
    latest = recent[-1]
    
    # Calculate some trends
    trend_str = ""
    if len(recent) > 1:
        first = recent[0]
        # Make sure values are not null before diffing
        if latest.get('temperature') is not None and first.get('temperature') is not None:
            temp_diff = latest['temperature'] - first['temperature']
            humid_diff = latest['humidity'] - first['humidity']
            soil_diff = latest['soil'] - first['soil']
            trend_str = f"Over the last 10 readings: Temp changed by {temp_diff:.1f}°C, Humidity by {humid_diff:.1f}%, Soil Moisture by {soil_diff}."

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""
        You are an expert AI Agronomist for EcoMonitor Pro. 
        You are analyzing data for this specific crop: **{crop_type}**.
        
        Analyze the current farm conditions and trends, then give a short 2-sentence actionable advice tailored to {crop_type}.
        
        Current Data:
        Soil Moisture: {latest.get('soil')} (typically 0-1024, lower is wetter)
        Temperature: {latest.get('temperature')}°C
        Humidity: {latest.get('humidity')}%
        Rain: {latest.get('rain')}
        Pump is currently: {latest.get('pump')}
        
        Trend Analysis:
        {trend_str}
        """
        response = model.generate_content(prompt)
        return jsonify({"suggestion": response.text.strip()})
    except Exception as e:
        return jsonify({"suggestion": f"AI Error: Ensure you have provided a valid GEMINI_API_KEY. Detailed error: {str(e)}"})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")
    history = data.get("history", [])
    crop_type = data.get("crop", "General plants")
    
    recent = get_history_readings(5)
    latest = recent[-1] if recent else {}
    
    sys_instruction = f"""You are a helpful AI Agronomist Chatbot for EcoMonitor Pro.
    You assist the farmer with their crops. 
    They are currently growing: {crop_type}.
    Current live data: Temp: {latest.get('temperature')}°C, Humid: {latest.get('humidity')}%, Soil: {latest.get('soil')}, Pump: {latest.get('pump')}.
    Keep responses brief, friendly, and highly practical."""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=sys_instruction)
        
        formatted_history = []
        for msg in history:
            formatted_history.append({
                "role": "user" if msg['role'] == 'user' else "model",
                "parts": [msg['content']]
            })
            
        chat_session = model.start_chat(history=formatted_history)
        response = chat_session.send_message(message)
        
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"AI Error: {str(e)}"}), 500

# ------------------ Run ------------------

if __name__ == "__main__":
    init_db()
    
    serial_thread_running = True
    threading.Thread(target=read_serial, daemon=True).start()
    
    app.run(debug=True, use_reloader=False)
