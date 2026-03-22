# 🏥 CareBridge: Autonomous Clinical AI & Telemedicine Ecosystem

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-Backend-darkgreen.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Microservices-teal.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)
![Gemini AI](https://img.shields.io/badge/Google_Gemini-2.5_Flash-orange.svg)
![WebRTC](https://img.shields.io/badge/WebRTC-Telemedicine-purple.svg)

**CareBridge** is an enterprise-grade hospital appointment and record management system that entirely automates patient triage using Large Language Models (LLMs) and mathematically secures patient medical records using strictly enforced Temporal Privacy Locks.

---

## 🚀 Why It Was Built (The Problem & Solution)

**The Problem:** Traditional hospital workflows are broken. Patients face massive friction trying to book appointments through manual receptionists. Doctors suffer from "digital burnout" due to cluttered Electronic Medical Record (EMR) systems. Furthermore, legacy EMRs inherently violate patient privacy by giving doctors *permanent* access to sensitive files long after a consultation ends.

**The Solution:** CareBridge introduces an **Autonomous Triage Agent** that lets patients book appointments instantly using natural language. It introduces a **Temporal Privacy Engine** that grants doctors access to patient EMRs for exactly 4 hours post-consultation, and permanently locks medical reports from edits after 24 hours to ensure legal immutability. 

---

## ✨ Core Features

### 👤 For Patients (Zero-Friction Access)
* **Autonomous AI Triage:** No more dropdown menus. Patients type symptoms in natural language (e.g., *"I have severe chest pain"*), and the Gemini AI autonomously routes them to the correct specialist (Cardiology) and executes the database booking.
* **Native Telemedicine:** Patients join secure, peer-to-peer WebRTC video consultations directly from their dashboard—no external apps or Zoom links required.
* **Secure Medical Vault:** Patients can upload previous lab reports (PDF/Images) which are encrypted and heavily restricted from unauthorized viewing.

### 👨‍⚕️ For Doctors (Zero-Friction Command Center)
* **Minimalist UI/UX:** A clean, Tailwind CSS-powered dashboard that strictly separates the "Pending Approvals" queue from the "Confirmed Schedule," drastically reducing cognitive load.
* **One-Click Approvals:** Doctors review the AI's summarized triage notes and approve appointments instantly.
* **Temporal EMR Unlocking:** Patient medical history is physically locked until the consultation begins. 
* **Aggressive Compliance Alerts:** The dashboard prominently flags missing medical reports with a red "Upload Required" badge.

### 🛡️ For System / Admin (Security & Compliance)
* **4-Hour Privacy Lock:** Enforces the Digital Personal Data Protection (DPDP) Act by physically revoking a doctor's access to a patient's file exactly 4 hours after the appointment starts.
* **24-Hour Immutability Lock:** Ensures medical and legal integrity by permanently locking a submitted medical diagnosis from edits exactly 24 hours after submission.
* **Asynchronous AI Routing:** FastAPI microservices handle the heavy LLM traffic so the main Django hospital database never freezes.

---

## ⚙️ How It Works (The Working Model)

1. **Patient Triage:** A patient logs in and describes their symptoms to the AI Chatbot.
2. **AI Execution:** The Gemini 2.5 Flash API parses the text, identifies the correct department, and commits a `Pending` appointment to the PostgreSQL database.
3. **Clinical Approval:** The designated doctor reviews the pending queue on their Command Center and confirms the slot.
4. **Telemedicine & Unlock:** At the scheduled time, the WebRTC video connects. The backend simultaneously unlocks the patient's EMR for the strict 4-hour window.
5. **Documentation & Lock:** The doctor authors the clinical report. Exactly 24 hours later, the backend triggers an immutable edit lockout.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Frontend UI/UX** | HTML5, CSS3, Vanilla JavaScript, Tailwind CSS |
| **Core Backend Framework** | Django (Python) |
| **Asynchronous API Gateway**| FastAPI |
| **Relational Database** | PostgreSQL |
| **Artificial Intelligence** | Google Gemini 2.5 Flash API |
| **Telemedicine** | WebRTC APIs (with STUN/TURN server traversal) |
| **Security** | JSON Web Tokens (JWT), AES-256 Hashing |

---

## 💻 Local Installation & Setup

To run CareBridge on your local machine, follow these steps:

**1. Clone the repository**
```bash
git clone [https://github.com/SHIVASHANKAR-KODURI/VitalSync.git](https://github.com/SHIVASHANKAR-KODURI/VitalSync.git)
cd VitalSync

**2. Create a Virtual Environment**

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

**3. Install Dependencies**

```bash
pip install -r requirements.txt
```

**4. Setup Environment Variables**
Create a `.env` file in the root directory and add your credentials:

```env
GEMINI_API_KEY=your_google_gemini_api_key
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=your_django_secret_key
```

**5. Apply Database Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

**6. Run the Servers**
You need to run both the Django core server and the FastAPI microservice simultaneously.

*Terminal 1 (Django Core):*

```bash
python manage.py runserver
```

*Terminal 2 (FastAPI AI Router):*

```bash
uvicorn api.main:app --reload --port 8001
```

-----

## 👥 The Team

This Capstone Project was developed by students at the **School of Computer Science and Artificial Intelligence, SR University**:

  * Siddhartha Namilikonda (2203A52110)
  * Shiva Shankar Koduri (2203A52154)
  * Rahul Sunny Satthu (2203A52175)
  * Rahul Thadishetty (2203A52193)
  * Hrudai Gogikar (2203A52022)
  * Harshavardhan Arikala (2203A52234)


-----

*Built to Democratize Healthcare Access and Protect Patient Privacy.*
