# 🧠 Identra AI

### AI-Powered Digital Identity & Document Intelligence Platform

**Identra AI** is an AI-powered digital identity system designed to organize, classify, search, and manage a user's academic and professional documents in one centralized platform.

Instead of keeping certificates, resumes, identity documents, and professional records scattered across folders and devices, Identra AI transforms them into a **structured, searchable, and intelligent digital identity**.

🌐 **Live Demo:** https://identra-ai.onrender.com/

---

## 🚀 Key Features

### 📁 Intelligent Document Management

* Upload and manage documents from a centralized dashboard.
* Organize documents into meaningful categories.
* View and manage uploaded documents easily.
* Maintain a structured digital document repository.

### 🤖 AI-Powered Document Classification

Identra AI automatically analyzes uploaded documents and identifies their appropriate category.

Supported categories include:

* 🎓 Education
* 💼 Career
* 📜 Certificates
* 🪪 Personal Documents
* 🚗 Transportation
* 🏆 Achievements
* 📄 Other Professional Documents

The classification system uses **phrase-based matching and confidence scoring** to improve document categorization accuracy.

### 🔍 Smart Document Search

Search through stored documents quickly using relevant document information and metadata.

### 👤 Digital Identity Profile

Create a centralized digital identity containing:

* Personal information
* Academic qualifications
* Professional experience
* Certifications
* Achievements
* Important documents

### 📊 Dashboard & Analytics

The dashboard provides an overview of the user's digital identity and stored documents.

It can display:

* Total documents
* Document categories
* Recent uploads
* Profile information
* Document statistics

### 🔐 Authentication & Security

* User registration and login
* Session-based authentication
* Protected dashboard routes
* Environment-based configuration
* Sensitive configuration excluded from version control

### 🎨 Modern Web Interface

* Responsive design
* Clean dashboard
* Navigation system
* Document management interface
* Mobile-friendly layouts

### ☁️ Deployment Ready

The project includes deployment configuration for cloud hosting.

Included deployment files:

* `Dockerfile`
* `Procfile`
* `render.yaml`
* `wsgi.py`
* `DEPLOYMENT_GUIDE.md`

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │       User           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Web Interface      │
                    │ HTML / CSS / JS      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Flask App       │
                    │     Application      │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌────────────┐   ┌─────────────┐   ┌──────────────┐
       │   Routes   │   │  Services   │   │    Utils     │
       └─────┬──────┘   └──────┬──────┘   └──────┬───────┘
             │                 │                  │
             └─────────────────┼──────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │      Database        │
                    │   SQLite / SQL ORM   │
                    └──────────────────────┘
```

---

# 🛠️ Technology Stack

| Layer             | Technology                                  |
| ----------------- | ------------------------------------------- |
| Frontend          | HTML5, CSS3, JavaScript                     |
| UI                | Bootstrap                                   |
| Backend           | Python, Flask                               |
| Database          | SQLite                                      |
| ORM               | SQLAlchemy                                  |
| Authentication    | Flask-Login                                 |
| AI / Intelligence | Document Classification & AI-ready services |
| Deployment        | Render                                      |
| Containerization  | Docker                                      |
| Server            | Gunicorn                                    |
| Version Control   | Git & GitHub                                |

---

# 📂 Project Structure

```text
Identra-AI/
│
├── database/
│   └── models/
│       ├── chat.py
│       ├── document.py
│       ├── embedding.py
│       ├── google_drive.py
│       ├── graph.py
│       ├── notification.py
│       ├── timeline.py
│       ├── user.py
│       └── __init__.py
│
├── migrations/
│
├── routes/
│   ├── auth routes
│   ├── document routes
│   ├── dashboard routes
│   └── other application routes
│
├── services/
│   └── application services
│
├── static/
│   ├── css/
│   ├── js/
│   └── assets/
│
├── templates/
│   └── HTML templates
│
├── utils/
│   └── document classification utilities
│
├── app.py
├── config.py
├── extensions.py
├── wsgi.py
│
├── landing.html
├── about.html
├── base.html
│
├── Dockerfile
├── Procfile
├── render.yaml
├── requirements.txt
│
├── PROJECT_DOCUMENTATION.md
├── DEPLOYMENT_GUIDE.md
│
├── test_all_pages.py
├── test_auth_and_routes.py
│
├── .env.example
├── .gitignore
└── .dockerignore
```

---

# ⚙️ Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/kamalikasenthilnaathan09/Identra-AI.git
```

Move into the project directory:

```bash
cd Identra-AI
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root.

Use `.env.example` as the template.

Example:

```env
SECRET_KEY=your-secret-key
FLASK_ENV=development
DATABASE_URL=sqlite:///instance/identra_ai.db
PORT=5000
```

> ⚠️ Never commit your real `.env` file or API keys to GitHub.

---

## 5. Initialize the Database

Run the database initialization or migration process provided in the project.

```bash
python app.py
```

If your project requires database initialization separately, follow the instructions in `DEPLOYMENT_GUIDE.md`.

---

## 6. Run the Application

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

---

# 🧪 Testing

Identra AI includes automated test scripts for checking application pages, authentication, and routes.

Run:

```bash
python test_all_pages.py
```

Authentication and route tests:

```bash
python test_auth_and_routes.py
```

---

# ☁️ Deployment

Identra AI is configured for deployment using **Render**.

Deployment-related files include:

```text
Dockerfile
Procfile
render.yaml
wsgi.py
DEPLOYMENT_GUIDE.md
```

### Live Application

🌐 **https://identra-ai.onrender.com/**

---

# 🔐 Security

Identra AI follows several security practices:

* Environment variables for sensitive configuration
* `.gitignore` protection for local secrets
* Session-based authentication
* Protected application routes
* Server-side validation
* Separate production configuration

**Important:** Never place passwords, API keys, OAuth secrets, or private credentials directly inside source code.

---

# 🔮 Future Enhancements

The platform can be extended with advanced AI capabilities such as:

### 🧾 OCR

Automatically extract text from scanned documents and images.

### 📄 Resume Parsing

Extract structured information from resumes, including:

* Skills
* Education
* Experience
* Projects
* Certifications

### 🧠 Semantic Search

Use sentence embeddings to search documents based on **meaning**, rather than exact keywords.

### 🔗 Knowledge Graph

Build relationships between:

```text
User
 │
 ├── Education
 │    ├── Degree
 │    ├── University
 │    └── Certificates
 │
 ├── Career
 │    ├── Internship
 │    ├── Skills
 │    └── Experience
 │
 └── Achievements
      ├── Awards
      └── Certifications
```

### ☁️ Google Drive Integration

Allow users to import and synchronize documents from Google Drive.

### 🤖 AI Assistant

An intelligent assistant could answer questions such as:

> "What certifications do I have?"

> "Show my internship documents."

> "Which skills are mentioned in my resume?"

> "When did I complete my degree?"

---

# 🎯 Problem Statement

Modern students and professionals maintain a large number of digital documents such as resumes, certificates, academic records, internship documents, identity documents, and achievement records.

These files are often scattered across different folders, devices, cloud storage platforms, and email accounts.

This makes it difficult to:

* Locate important documents quickly
* Maintain an organized digital identity
* Search across multiple documents
* Understand relationships between qualifications and achievements
* Reuse information for resumes, applications, and professional opportunities

---

# 💡 Solution

**Identra AI** provides a centralized digital identity platform that brings important academic and professional information into one intelligent repository.

The system combines:

**Document Management + Classification + Search + Digital Identity + AI-ready Intelligence**

to create a unified personal knowledge system.

---

# 🌟 Vision

> **"One person. One intelligent digital identity."**

Identra AI aims to become an intelligent personal document and identity management platform that helps students and professionals organize their digital records and access important information whenever they need it.

---

# 👩‍💻 Developer

**Kamalika Y.S**

B.Tech Artificial Intelligence & Data Science

GitHub:
https://github.com/kamalikasenthilnaathan09

---

# 📜 License

This project is currently developed as an academic/hackathon project.

---

## ⭐ Support the Project

If you find Identra AI interesting, consider giving the repository a ⭐ on GitHub.

**Repository:**
https://github.com/kamalikasenthilnaathan09/Identra-AI
