# Integrated Patient Care Management System (IPCMS)

A comprehensive healthcare management platform built with **Streamlit** that integrates patient records, doctor workflows, AI-powered assistance, and voice-based interaction into a single unified system.

---

## 🌟 Features

- **Patient Management** — Register, view, update, and manage patient records with secure authentication.
- **Doctor Portal** — Doctor-specific dashboards with prescription management and patient history.
- **Admin Console** — Add/manage medicines, oversee users, and configure system settings.
- **AI Care Assistant** — Conversational chatbot powered by **Groq / LangChain** for intelligent healthcare queries.
- **Voice Assistant** — Voice-enabled chatbot for hands-free interaction.
- **Email Notifications** — SMTP-based credential delivery to doctors on registration.
- **Medical Reports** — PDF report generation using **ReportLab**.
- **Database Integration** — MySQL backend via **PyMySQL** with secure credential storage.
- **Authentication** — Role-based access (admin / doctor / patient) with Google OAuth support.

---

## � Tech Stack

| Layer       | Technology                          |
|-------------|--------------------------------------|
| Frontend    | Streamlit                            |
| Backend     | Python                               |
| Database    | MySQL (via PyMySQL)                  |
| AI / LLM    | Groq + LangChain                     |
| Voice       | Voice-enabled chatbot (STT / TTS)    |
| Email       | SMTP (Gmail App Password)            |
| Reports     | ReportLab, pdfplumber                |
| Auth        | Google OAuth 2.0                     |

---

## � Project Structure

Integrated_Patient_Care_Management_System/
├── app.py                    # Main Streamlit entry point
├── auth.py                   # Authentication & role handling
├── db.py                     # Database utilities
├── db_config.py              # DB connection configuration
├── chatbot.py                # AI chatbot logic
├── voice_chatbot.py          # Voice assistant module
├── ai_care.py                # AI care / LangChain integration
├── email_service.py          # SMTP email service
├── generate_ppt.py           # PPT report generation
├── add_medicines_admin.py    # Admin medicine management
├── update_admin.py           # Admin user management
├── check_file.py             # Utility script
├── pages/                    # Streamlit multi-page UI
├── patient_care/             # Patient-care-specific modules
├── static/                   # Static assets (CSS, images)
├── background/               # Background images
├── Medicine_Images/          # Medicine image assets
├── .streamlit/               # Streamlit config (theme, secrets)
├── patient_care.db           # Local SQLite fallback DB
├── users_db.json             # Local users store
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
└── README.md                 # You are here

---

## ⚙️ Prerequisites

- Python **3.9+**
- pip (Python package manager)
- MySQL server (optional — SQLite fallback included)
- A **Groq API key** — https://console.groq.com
- (Optional) **Google OAuth credentials** — https://console.cloud.google.com
- (Optional) **Gmail App Password** for SMTP emails — https://myaccount.google.com/apppasswords

---

## 🚀 Installation & Setup

### 1. Clone the repository

git clone https://github.com/Nikhil27092006/Integrated_Patient_Care_Management_System.git
cd Integrated_Patient_Care_Management_System

2. Create
Interrupted · What should Claude do instead?

❯ for this project readme so that i can just copy and paste it

# 🏥 Integrated Patient Care Management System (IPCMS)

A comprehensive healthcare management platform built with **Streamlit** that integrates patient records, doctor workflows, AI-powered assistance, and voice-based interaction into a single unified system.

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Usage](#-usage)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🔎 Overview

The **Integrated Patient Care Management System** is a full-stack healthcare web application designed to streamline the interaction between **patients**, **doctors**, and **administrators**. It brings together electronic health records, prescription management, AI-driven assistance, voice-enabled interaction, and automated email notifications into one secure platform.

---

## ✨ Features

### 👤 Patient
- Secure registration and login
- View personal medical history
- Book / manage appointments
- Access prescriptions and reports
- Interact with AI chatbot for health queries
- Voice-based assistant support

### 👨‍⚕️ Doctor
- Dedicated doctor dashboard
- View assigned patients and history
- Create and manage prescriptions
- Receive new patient credentials via email
- AI-assisted clinical queries

### 🛠️ Admin
- Manage users (patients & doctors)
- Add / update medicines inventory
- Generate system reports (PDF / PPT)
- View analytics and activity logs
- Manage roles and permissions

### 🤖 AI & Voice
- **AI Care Assistant** powered by **Groq + LangChain**
- **Voice Chatbot** for hands-free interaction
- Natural-language medical Q&A

### 📧 Notifications
- SMTP-based email service (Gmail)
- Automatic credential delivery to doctors
- Configurable email templates

### � Reports
- PDF generation via **ReportLab**
- PowerPoint summary generation
- Medical record extraction via **pdfplumber**

---

## � Tech Stack

| Layer        | Technology                          |
|--------------|--------------------------------------|
| Frontend     | Streamlit (Python)                   |
| Backend      | Python 3.9+                          |
| Database     | MySQL (PyMySQL) / SQLite fallback    |
| AI / LLM     | Groq API + LangChain                 |
| Voice        | Voice-enabled chatbot (STT / TTS)    |
| Email        | SMTP (Gmail App Password)            |
| Auth         | Google OAuth 2.0 + local auth        |
| Reports      | ReportLab, pdfplumber, python-pptx   |
| Encryption   | cryptography (Fernet)                |

---

## 📁 Project Structure

Integrated_Patient_Care_Management_System/
├── app.py                        # Main Streamlit entry point
├── auth.py                       # Authentication & role handling
├── db.py                         # Database utilities
├── db_config.py                  # DB connection configuration
├── chatbot.py                    # AI chatbot logic
├── voice_chatbot.py              # Voice assistant module
├── voice_chatbot_cleanup.py      # Voice module helpers
├── ai_care.py                    # AI care / LangChain integration
├── email_service.py              # SMTP email service
├── generate_ppt.py               # PPT report generation
├── add_medicines_admin.py        # Admin: medicine management
├── update_admin.py               # Admin: user management
├── check_file.py                 # Utility script
├── pages/                        # Streamlit multi-page UI
├── patient_care/                 # Patient-care modules
├── static/                       # Static assets (CSS, images)
├── background/                   # Background images
├── Medicine_Images/              # Medicine image assets
├── .streamlit/                   # Streamlit config (theme, secrets)
├── patient_care.db               # Local SQLite DB
├── users_db.json                 # Local users store
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
└── README.md                     # You are here

---

## ✅ Prerequisites

Make sure you have the following installed:

- **Python 3.9+**
- **pip** (Python package manager)
- **MySQL Server** *(optional — SQLite fallback available)*
- **Git**

You will also need API keys / credentials:

- 🔑 **Groq API Key** → https://console.groq.com
- 🔑 **Google OAuth Client ID & Secret** *(optional)* → https://console.cloud.google.com
- 📧 **Gmail App Password** *(for SMTP)* → https://myaccount.google.com/apppasswords

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

git clone https://github.com/Nikhil27092006/Integrated_Patient_Care_Management_System.git
cd Integrated_Patient_Care_Management_System

2️⃣ Create a Virtual Environment

python -m venv venv

Activate it:

- Windows
venv\Scripts\activate
- macOS / Linux
source venv/bin/activate

3️⃣ Install Dependencies

pip install -r requirements.txt

---
🔐 Configuration

1. Environment Variables

Copy the example file and fill in your credentials:

cp .env.example .env

Edit .env:

env
# Groq (AI / LLM)
GROQ_API_KEY=your_groq_api_key_here

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8501

# Email / SMTP (Gmail recommended)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_gmail@gmail.com
SMTP_PASSWORD=your_16_char_app_password
SMTP_FROM_NAME=PCMHS — Patient Care Management System for Healthcare Services

# App URL shown in doctor credential emails
APP_LOGIN_URL=http://localhost:8501

2. Database

- Default: the app falls back to a local SQLite database (patient_care.db).
- MySQL (optional): configure your MySQL credentials inside db_config.py and ensure the server is running.

---
▶️ Running the Application

Start the Streamlit server:

streamlit run app.py

The app will open at:

http://localhost:8501

---
💡 Usage

1. Open the app in your browser.
2. Sign up as a Patient, Doctor, or Admin.
3. Log in with your credentials (or via Google OAuth if configured).
4. Explore role-specific dashboards:
  - Patients → view history, prescriptions, chat with AI
  - Doctors → manage patients, create prescriptions
  - Admins → manage users, medicines, view analytics
5. Try the AI Care Assistant and Voice Chatbot for interactive help.

---
🤝 Contributing

Contributions are welcome! 🎉

1. Fork the repository
2. Create a new branch
git checkout -b feature/your-feature-name
3. Make your changes
4. Commit your changes
git commit -m "Add: your feature description"
5. Push to your branch
git push origin feature/your-feature-name
6. Open a Pull Request

Please ensure your code follows the existing style and includes appropriate documentation.

---
📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

---
📬 Contact

Author: Nikhil
GitHub: @Nikhil27092006 (https://github.com/Nikhil27092006)

For questions or support, please open an issue on the GitHub repository.

---
⭐ If you find this project useful, please consider giving it a star!
