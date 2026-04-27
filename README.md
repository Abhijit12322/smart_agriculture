<div align="center">

# 🌿 EcoMonitor Pro
## Intelligent Farm Management & AI Agronomist System

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-22c55e?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Backend-Flask%20%2B%20Python-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/AI-Gemini%202.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/Hardware-Arduino%20%2F%20ESP32-00979D?style=for-the-badge&logo=arduino&logoColor=white" />
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
</p>

<br/>

> **EcoMonitor Pro** bridges the gap between physical agricultural hardware and advanced Artificial Intelligence.
> Live sensor telemetry from the field. A context-aware AI agronomist that *already knows* your farm's conditions.
> A dashboard built to look as intelligent as it actually is.

<br/>

</div>

---

## 🧭 What Is EcoMonitor Pro?

Most IoT dashboards are **passive** — they show numbers and leave the thinking to you.

**EcoMonitor Pro is different.** It ingests live sensor data (soil moisture, temperature, humidity, rain status) from an Arduino or ESP32 via serial, stores it in a local database, visualises it on a premium glassmorphism dashboard — and then hands it all silently to a **Gemini 2.5 Flash AI agronomist** that can answer questions like:

> *"My soil moisture is at 800 right now — should I turn on the pump?"*
> *"Is today's humidity going to stress my crops?"*
> *"Show me what's changed in the last hour."*

The AI already knows. It's reading your farm in real time.

<div align="center">

| ⚡ Real-Time Telemetry | 🤖 AI Agronomist | 📈 Historical Trends |
|:----------------------:|:----------------:|:--------------------:|
| Soil · Temp · Humidity · Rain streamed live every 1.5 seconds | Gemini 2.5 Flash with your live sensor readings silently injected as context | SQLite logs last 100 readings; Chart.js renders auto-updating timelines |

</div>



## 🗺️ System Architecture

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                          ECOMONITOR PRO                                   ║
║               Intelligent Farm Management & AI Agronomist                 ║
╚═══════════════════════════════════════════════════════════════════════════╝


 ┌──────────────────────────────────────────────────────────────────────┐
 │       🔌  HARDWARE LAYER  —  Arduino / ESP32                        │
 │                                                                      │
 │   Soil Moisture Sensor ──┐                                           │
 │   Rain Sensor ───────────┼──► Microcontroller ──► Serial (9600 baud) │
 │   DHT11 (Temp + Hum) ────┘                                           │
 │                                                                      │
 │   Output format: JSON payload per reading                            │
 │   { "soil": 800, "rain": 0, "temp": 31.5, "hum": 72.0,               │
 │     "pump": "ON" }                                                   │
 └────────────────────────────────┬─────────────────────────────────────┘
                                  │  USB Serial
                                  ▼
 ┌──────────────────────────────────────────────────────────────────────┐
 │          🧠  FLASK BACKEND  —  app.py  (Multi-threaded)             │
 │                                                                      │
 │  ┌─────────────────────────────────────────────────────────────────┐ │
 │  │  SERIAL THREAD  (daemon, pyserial)                              │ │
 │  │  └── Continuously reads JSON from microcontroller               │ │
 │  │       threading.Lock() prevents collision with API requests     │ │
 │  │       Inserts each reading → SQLite  (rolling 100-record log)   │ │
 │  └──────────────────────────────┬──────────────────────────────────┘ │
 │                                 │                                    │
 │  ┌─────────────────────────────────────────────────────────────────┐ │
 │  │  SQLITE DATABASE  —  sensor_data.db                             │ │
 │  │  └── Stores: soil, rain, temp, humidity, pump, timestamp        │ │
 │  │      Maintains last 100 readings for chart history & CSV export │ │
 │  └──────────────────────────────┬──────────────────────────────────┘ │
 │                                 │                                    │
 │  ┌─────────────────────────────────────────────────────────────────┐ │
 │  │  GEMINI AI ENGINE  (google-generativeai SDK)                    │ │
 │  │  └── On /api/chat request:                                      │ │
 │  │      1. Fetches latest live sensor reading from DB              │ │
 │  │      2. Silently prepends it to the system prompt               │ │
 │  │      3. Sends user message + context to Gemini 2.5 Flash        │ │
 │  │      4. Returns expert agronomic response to frontend           │ │
 │  └──────────────────────────────┬──────────────────────────────────┘ │
 │                                 │                                    │
 │  ╔══════════════ HTTP ROUTES ════════════════════════════════════╗   │
 │  ║  GET   /            →  home.html        Landing Page          ║   │
 │  ║  GET   /dashboard   →  dashboard.html   Core App UI           ║   │
 │  ║  GET   /docs        →  docs.html        User Manual           ║   │
 │  ║  GET   /ports       →  Available COM ports        (JSON)      ║   │
 │  ║  POST  /connect     →  Connect / Disconnect serial port       ║   │
 │  ║  GET   /data        →  Latest sensor reading      (JSON)      ║   │
 │  ║  GET   /history     →  Last 10 readings            (JSON)     ║   │
 │  ║  GET   /export      →  Full history CSV download              ║   │
 │  ║  POST  /api/chat    →  Gemini AI response          (JSON)     ║   │
 │  ╚═══════════════════════════════════════════════════════════════╝   │
 └──────────┬──────────────────────┬────────────────────┬───────────────┘
            │                      │                    │
            ▼                      ▼                    ▼
 ┌────────────────────┐  ┌────────────────────────┐  ┌─────────────────┐
 │    home.html       │  │   dashboard.html       │  │   docs.html     │
 │   LANDING PAGE     │  │     CORE APP UI        │  │  IN-APP DOCS    │
 │                    │  │                        │  │                 │
 │ • Deep gradient    │  │  SIDEBAR               │  │ • Arduino JSON  │
 │   mesh hero        │  │  ├── COM port select   │  │   format ref    │
 │ • Micro-animations │  │  ├── Connect toggle    │  │ • .env / API    │
 │ • Feature grid:    │  │  ├── Export CSV        │  │   key setup     │
 │   ─ Telemetry      │  │  └── Docs link         │  │ • AI chat guide │
 │   ─ AI Agronomist  │  │                        │  │ • CSV export    │
 │   ─ Analytics      │  │  MAIN PANEL            │  │   walkthrough   │
 │ • Sticky navbar    │  │  ├── Glassmorphism     │  │                 │
 │ • High-converting  │  │  │   sensor cards      │  └─────────────────┘
 │   CTA button       │  │  │   Soil·Temp·Hum·    │
 └────────────────────┘  │  │   Rain·Pump         │
                         │  ├── Animated progress │
                         │  │   bars + optimal    │
                         │  │   target ranges     │
                         │  ├── Last Synced clock │
                         │  │   (HH:MM:SS)        │
                         │  ├── Chart.js timeline │
                         │  │   (auto-updates,    │
                         │  │   theme-synced)     │
                         │  └── ☀️ / 🌙 toggle   │
                         │                        │
                         │  FLOATING AI WIDGET    │
                         │  ├── Bottom-right      │
                         │  ├── Gemini 2.5 Flash  │
                         │  ├── Live sensor data  │
                         │  │   injected silently │
                         │  ├── Session history   │
                         │  └── Quick Action chips│
                         └────────────────────────┘


 ─────────────────── THEMING SYSTEM ────────────────────────────────

   User clicks ☀️ / 🌙 toggle
         │
         ▼
   [data-theme="dark"] set on <html> root
         │
         ├── CSS variables swap  →  --bg-body, --text-main, --card-bg …
         ├── Chart.js grid lines & font colors auto-sync
         ├── Floating AI chat widget re-skins to match
         └── Preference saved to localStorage  (persists on reload)


 ─────────────────── DATA FLOW ─────────────────────────────────────

   Microcontroller (Arduino / ESP32)
        │
        │  JSON via Serial (9600 baud)
        ▼
   Flask Serial Thread
        ├── Continuous data ingestion (pyserial)
        ├── Thread-safe handling (threading.Lock)
        └── Stores latest readings
                │
                ▼
        SQLite Database
        (soil · temp · humidity · rain · pump · timestamp)
                │
        ┌───────┼──────────────────────────────────────────────┐
        │       │                                              │
        ▼       ▼                                              ▼
   /data      /history                                   /export
 (latest)   (recent logs)                             (CSV download)

        │
        ▼
   Dashboard (Frontend JS)
        ├── Polls /data + /history every 1.5 seconds
        ├── Updates UI (cards, charts, status)
        └── Non-blocking real-time refresh

        │
        ▼
   /api/chat  (AI Interaction Layer)
        ├── Receives user query
        ├── Fetches latest sensor snapshot
        ├── Injects context silently
        ▼
   Gemini 2.5 Flash
        │
        ▼
   Intelligent Agronomic Response

```


## 📁 Project Structure

```
Project.../                         ← project root
│
├── Arduino_Code/                  # Microcontroller code (Arduino / ESP32)
│   └── sketch.ino                 # Sensor reading + JSON serial output
│
├── templates/
│   ├── dashboard.html            # Core monitoring dashboard (glassmorphism UI)
│   ├── docs.html                 # In-app user manual & setup guide
│   └── home.html                 # Commercial landing page
│
├── .env                          # GEMINI_API_KEY  ← never commit this
├── .env.example                  # Safe template showing required keys
├── app.py                        # Flask backend — routes, serial thread,
│                                # SQLite DB, threading.Lock(), Gemini AI
├── data.json                     # Sensor data buffer / config
├── models.txt                    # Model references / requirements notes
├── README.md                     # Project documentation
└── sensor_data.db                # SQLite database (auto-created on first run)

```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- Arduino or ESP32 printing JSON to Serial at **9600 baud**
- A free [Gemini API key](https://aistudio.google.com)


### Step 1 — Clone
```bash
git clone https://github.com/your-username/ecomonitor-pro.git
cd ecomonitor-pro
```

### Step 2 — Install dependencies
```bash
pip install flask pyserial google-generativeai python-dotenv
```

### Step 3 — Configure API key
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Step 4 — Flash the Arduino / ESP32
Ensure your microcontroller prints JSON to Serial at 9600 baud:
```json
{"soil": 800, "rain": 0, "temp": 31.5, "hum": 72.0, "pump": "ON"}
```

### Step 5 — Run
```bash
python app.py
```

### Step 6 — Open
```
http://127.0.0.1:5000
```
→ Click **Launch Dashboard** → Select COM port → **Connect** ✅

---

## ✨ Features

<details>
<summary><b>🏠 &nbsp; Commercial Landing Page &nbsp;<code>/</code></b></summary>
<br/>

A polished, high-converting hero page designed to introduce the product with confidence.

- Deep **gradient mesh background** with micro-animations
- Bold headline typography and a prominent **"Launch Dashboard"** CTA
- **Feature showcase grid** — Real-Time Telemetry · AI Agronomist · Predictive Analytics
- **Sticky top navbar** with smooth scroll navigation

</details>

<details>
<summary><b>📊 &nbsp; Real-Time Telemetry Dashboard &nbsp;<code>/dashboard</code></b></summary>
<br/>

The core of EcoMonitor Pro — everything you need at a glance.

- **Fixed sidebar** — COM port selector, connect/disconnect toggle, CSV export, docs link. Sidebar keeps the main panel clutter-free
- **Glassmorphism sensor cards** — translucency, background blur, and neon accent lines for Soil · Temperature · Humidity · Rain · Pump Status
- **Animated horizontal progress bars** with live readings and **optimal target range labels** per sensor
- **"Last Synced" clock** — shows exact `HH:MM:SS` of the most recent hardware ping, confirming live connection
- **Chart.js timeline** — auto-updating historical graph; colors dynamically bind to the active theme
- **Day / Night toggle** — CSS variable system swaps the entire UI; chart colors sync; preference saved via `localStorage`

</details>

<details>
<summary><b>🤖 &nbsp; Floating AI Agronomist</b></summary>
<br/>

Not just a chatbot — a farming expert that's already watching your sensors.

- **Persistent floating widget** in the bottom-right corner, always accessible
- Powered by **Google Gemini 2.5 Flash**
- Every message silently includes your **exact live sensor readings** as context — no need to describe what's happening, the AI already knows
- **Quick Action chips** for instant analysis without typing (e.g. *"Should I irrigate now?"*)
- Maintains full **session conversation history**
- Dynamically re-skins with **Day / Night mode**

> *Example: "I can see your soil moisture is at 800 (very dry) right now — you should turn on the pump."*

</details>

<details>
<summary><b>📚 &nbsp; In-App Documentation &nbsp;<code>/docs</code></b></summary>
<br/>

Everything a user needs to get set up, without leaving the app.

- Arduino / ESP32 JSON serial format reference
- Step-by-step `.env` file and `GEMINI_API_KEY` configuration guide
- AI chat usage walkthrough
- CSV export instructions

</details>

<details>
<summary><b>📤 &nbsp; CSV Data Export &nbsp;<code>/export</code></b></summary>
<br/>

- One-click download of the **complete sensor history** (last 100 readings) as `.csv`
- Ready for Excel, Google Sheets, or further data analysis

</details>



## 🛠️ Tech Stack

<div align="center">

| Layer | Technology |
|:------|:-----------|
| **Backend** | ![Python](https://img.shields.io/badge/Python_3.x-3776AB?style=flat-square&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) |
| **Hardware I/O** | ![pyserial](https://img.shields.io/badge/pyserial-serial_comm-00979D?style=flat-square) ![Arduino](https://img.shields.io/badge/Arduino%20%2F%20ESP32-00979D?style=flat-square&logo=arduino&logoColor=white) |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) |
| **AI Engine** | ![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white) |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3_%2B_Variables-1572B6?style=flat-square&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/Vanilla_JS-F7DF1E?style=flat-square&logo=javascript&logoColor=black) |
| **Charts** | ![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=flat-square&logo=chartdotjs&logoColor=white) |
| **Config** | ![dotenv](https://img.shields.io/badge/.env_%2F_python--dotenv-ECD53F?style=flat-square) |

</div>



## 🔮 Roadmap

```
 ✅  Live sensor telemetry (soil, temp, humidity, rain)
 ✅  Automated pump control with relay logic
 ✅  Gemini 2.5 Flash AI agronomist with live context injection
 ✅  Glassmorphism dashboard with animated progress bars
 ✅  Day / Night theme with localStorage persistence
 ✅  CSV export of full sensor history
 ✅  In-app documentation page
 ✅  Thread-safe serial reading (threading.Lock)

 ⬜  Cloud deployment  (local Serial → MQTT / WebSockets)
 ⬜  Actuator control  (send commands back to Arduino from dashboard)
 ⬜  User authentication & multi-farm support
 ⬜  SMS / email alerts on critical threshold breach
 ⬜  ML-based predictive irrigation scheduling
```

---

## ⚠️ Important Notes

> 🔐 **Never commit your `.env` file.** Add it to `.gitignore` immediately.
> Your `GEMINI_API_KEY` must stay local and private.

> ⚡ **Never power the water pump from Arduino's 5V / Vin pins.**
> Always use a dedicated external 12V DC supply switched through the relay module.

---

<div align="center">

<br/>

*EcoMonitor Pro — Transforming raw IoT data into intelligent, actionable farming insights.*

**Built with 💧 for sustainable agriculture · ECE Department Project**

</div>