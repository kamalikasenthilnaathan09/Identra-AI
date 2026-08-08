# 🧠 Identra AI — Complete Project Documentation & Technical Specs

> **Identra AI (MemoryVerse AI)**: Next-Generation Digital Identity, Document Intelligence & Cognitive Knowledge Graph Engine.

---

## 📌 Executive Summary

**Identra AI** is a privacy-first, AI-powered digital identity management platform designed to index, structure, and verify personal, educational, professional, and project credentials. It converts unstructured documents (PDFs, images, marksheets, certificates, government IDs) into a structured **3D Knowledge Graph**, tracks document expiry & renewal deadlines (Aadhaar, Passports, Income Certificates), and provides multi-level encryption with 2FA and Passkey vault security.

---

## 🛠️ Technology Stack Architecture

| Layer | Technology | Purpose & Scope |
| :--- | :--- | :--- |
| **Backend Core** | Python 3.10+, Flask | Web framework, route orchestration, session security, REST APIs |
| **Database ORM** | SQLite3, Flask-SQLAlchemy | Relational database storage (`identra.db`) with dynamic schema migration (`db_repair.py`) |
| **OCR & AI Extraction** | PyTesseract, Tesseract OCR, Regex Engine | Extracting text, document numbers, issue dates, and expiry dates |
| **Knowledge Graph** | NetworkX, 3D Force Graph, GSAP | Constructing identity nodes (Skills, Projects, Education) and interactive 3D graph visualization |
| **Document Classification** | Rule-Based NLP & Keyword Intelligence | Auto-sorting uploads into Personal, Education, Professional, and Project folders |
| **Cloud Integration** | Google Drive API v3, Google OAuth 2.0 | Connecting external cloud storage with Quick Sync Mode (`kamalikasenthilnaathan@gmail.com`) |
| **Security & Auth** | Bcrypt, PyOTP (TOTP 2FA), Session Lock | Passkey PIN vault encryption, real-time 6-digit TOTP 2FA |
| **Frontend UI** | HTML5, Vanilla CSS3, JavaScript (ES6+) | Glassmorphic futuristic dark theme, responsive grid layouts |
| **Internationalization (i18n)** | Google Translate Dynamic Web Engine | 100% dynamic UI translation (Tamil `ta`, French `fr`, Spanish `es`, German `de`, English `en`) |

---

## 📂 System Directory Structure

```
MemoryVerse-AI/
├── app.py                      # Application Factory & Flask Entrypoint
├── config.py                   # Configuration Settings & Environment Keys
├── extensions.py               # SQLAlchemy Database Extensions
├── db_repair.py                # Schema Repair & Auto-Migration Script
├── test_all_pages.py           # Automated Audit Suite for all 14 Routes
├── database/
│   └── models/
│       ├── user.py             # User Account, 2FA & Passkey Model
│       ├── document.py         # Document, OCR & Expiry Info Model
│       ├── graph.py            # Knowledge Graph Nodes & Edges Model
│       ├── google_drive.py     # Connected Google Account & Drive Files Model
│       └── notification.py    # Notification & Alert Engine Model
├── routes/
│   ├── auth.py                 # Login, Registration, 2FA Verification
│   ├── dashboard.py            # Dashboard Console, Knowledge Graph, Profile, Settings
│   ├── documents.py            # Document Upload, Folder Vaults, Expiry Tracker
│   ├── google_drive.py        # Drive Cloud Integration & Quick Sync Mode
│   ├── api.py                  # Notifications, 2FA, Passkey & Search APIs
│   └── resume_builder.py       # AI Resume Generator & Export Engine
├── services/
│   ├── ocr.py                  # Tesseract OCR Processing Engine
│   ├── parser.py               # Expiry Date & Renewal Calculator (Aadhaar, Passport, Income Cert)
│   ├── ai.py                   # 4-Folder Vault Document Classifier
│   ├── graph.py                # Knowledge Graph Builder & NetworkX Sync
│   └── google_drive_service.py # Google Drive Download & Sync Service
├── static/
│   ├── css/                    # Glassmorphic Futuristic Stylesheets
│   └── js/                     # GSAP Animations, Toast System & Shortcuts
└── templates/                  # Jinja2 Frontend HTML Views (14 Pages)
```

---

## 🔥 Key Core Features & Modules

### 1. 🗂️ 4-Folder Vault Separation
Documents are automatically categorized into 4 isolated folder vaults:
* 👤 **Personal Documents**: Identity-related files (Aadhaar Card, Passport, Driver's License, Income Certificate, Voter ID).
* 🎓 **Education Documents**: Academic records, marksheets, degree diplomas, transcripts, educational certificates.
* 💼 **Professional Documents**: Resumes/CVs, internship letters, work experience letters, offer letters.
* 🚀 **Project Documents**: Project reports, code documentation, hackathon certificates, capstone achievements.

### 2. 🔐 Passkey Protected Personal Folder Vault
* **Security Lock**: Personal Vault is protected by a 4-digit Passkey PIN (Default: `1234`).
* **Interactive Modals**: Passkey PIN modal enforces authentication before displaying identity documents.
* **Passkey Management**: Users can update their Passkey PIN anytime via the modal or Settings.

### 3. 📄 Multimodal OCR & Strict Expiry Tracker
* **Date & Number Extraction**: Extracts Document Numbers (e.g. Aadhaar `8912 3412 9012`, Certificate `TN-72025041201`) and exact Issue/Expiry Dates.
* **Financial Year Validity**: Calculates 1-year Financial Year Expiry (`31/03/2026`) for **Income & Revenue Certificates**.
* **System Alerts**: Automatically triggers Expiry & Renewal notifications in the bell dropdown menu when renewal is due.

### 4. 🌐 100% Dynamic i18n Translation Engine
* Integrated dynamic translation engine supporting **Tamil (`ta`)**, **French (`fr`)**, **Spanish (`es`)**, **German (`de`)**, and **English (`en`)**.
* Translates 100% of all UI nodes instantly upon language selection in Settings.

### 5. 🧠 3D Interactive Knowledge Graph Engine
* 3x enlarged 3D node visualization with force-directed physics.
* Nodes represent User, Skills, Projects, Experience, and Certificates linked by dynamic semantic edges.
* Includes Zoom +, Zoom -, Fit View, and Reset controls.

### 6. ☁️ Google Drive Cloud Sync (`kamalikasenthilnaathan@gmail.com`)
* Connected to `kamalikasenthilnaathan@gmail.com`.
* **Quick Sync Mode**: Instant cloud browser to view and import Drive documents directly into AI memory.

### 7. 💡 Real-Time Skills Autocomplete Engine
* Real-time autocomplete suggestions dropdown on the Profile page populated with 70+ pre-loaded technical competencies.

### 8. 🛡️ Real-Time TOTP 2FA Security System
* Real-time toggle switch with secret key (`JBSWY3DPEHPK3PXP`) for TOTP Authenticator apps.

---

## 📊 Database Schema Summary

| Table | Primary Columns | Description |
| :--- | :--- | :--- |
| `users` | `id`, `username`, `email`, `password_hash`, `two_factor_enabled`, `personal_vault_passkey` | User account credentials & security settings |
| `documents` | `id`, `user_id`, `original_name`, `category`, `issue_date`, `expiry_date`, `doc_number` | Indexed documents with extracted OCR text & expiry dates |
| `knowledge_nodes` | `id`, `user_id`, `label`, `node_type`, `properties` | Graph nodes representing skills, projects, and credentials |
| `knowledge_edges` | `id`, `user_id`, `source_id`, `target_id`, `relation_type` | Graph relationships connecting identity nodes |
| `google_accounts` | `id`, `user_id`, `google_email`, `access_token`, `refresh_token` | Connected Google Drive OAuth accounts |
| `notifications` | `id`, `user_id`, `title`, `message`, `category`, `is_read` | System notifications & expiry alerts |

---

## ⚡ API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/documents/upload` | Upload & auto-categorize file into 4 Folders with OCR date extraction |
| `POST` | `/api/vault/verify-passkey` | Verify 4-digit Passkey PIN to unlock Personal Vault |
| `POST` | `/api/vault/set-passkey` | Set / Update Personal Vault Passkey PIN |
| `POST` | `/api/2fa/toggle` | Enable or disable TOTP 2FA real-time security |
| `GET` | `/google-drive/api/files` | List files in Google Drive cloud browser |
| `POST` | `/google-drive/api/import` | Import file from Google Drive into Identra AI memory |
| `GET` | `/api/notifications` | Fetch unread system notifications and expiry alerts |

---

## 🚀 Execution & Operational Audit

```bash
# 1. Run Automated 14-Route Audit Test Suite
.venv\Scripts\python.exe test_all_pages.py

# 2. Run Database Auto-Repair & Schema Migration
.venv\Scripts\python.exe db_repair.py

# 3. Launch Flask Server
.venv\Scripts\python.exe app.py
```
* **Local Web URL**: `http://127.0.0.1:5000/`
