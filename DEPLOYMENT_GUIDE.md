# 🚀 Identra AI – Complete Production Deployment Guide

This guide covers step-by-step instructions to deploy **Identra AI – Intelligent Digital Identity Companion** to various cloud hosts and production environments.

---

## 📋 Table of Contents
1. [Option 1: Free Cloud Hosting via Render.com (Recommended)](#-option-1-free-cloud-hosting-via-rendercom-recommended)
2. [Option 2: Railway.app Deployment](#-option-2-railwayapp-deployment)
3. [Option 3: Docker Container Deployment](#-option-3-docker-container-deployment)
4. [Option 4: Windows Production Service (Waitress)](#-option-4-windows-production-service-waitress)
5. [Option 5: Linux VPS (Nginx + Gunicorn + Systemd)](#-option-5-linux-vps-nginx--gunicorn--systemd)

---

## 🌟 Option 1: Free Cloud Hosting via Render.com (Recommended)

Render offers free web service hosting with automatic SSL (HTTPS).

### Steps:
1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Prepare Identra AI for Render deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/Identra-AI.git
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com) and log in.
   - Click **New +** → Select **Web Service**.
   - Connect your GitHub repository `Identra-AI`.
   - Set the following parameters:
     - **Name**: `identra-ai`
     - **Environment**: `Python 3`
     - **Region**: Select closest region (e.g. Oregon/Frankfurt/Singapore)
     - **Branch**: `main`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn wsgi:app`
   - Add Environment Variables under **Advanced**:
     - `SECRET_KEY`: `generate-a-strong-random-key-here`
     - `FLASK_ENV`: `production`
   - Click **Create Web Service**.

Render will automatically build and deploy your app at:  
`https://identra-ai.onrender.com`

---

## 🚂 Option 2: Railway.app Deployment

Railway supports 1-click deployment from GitHub repositories.

### Steps:
1. Sign in to [railway.app](https://railway.app).
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select your `Identra-AI` repository.
4. Railway will auto-detect Python, install dependencies from `requirements.txt`, and start `Procfile` (`gunicorn wsgi:app`).
5. Under **Settings** → **Networking**, click **Generate Domain** to get your public HTTPS URL.

---

## 🐳 Option 3: Docker Container Deployment

Use Docker to deploy containerized Identra AI on AWS ECS, DigitalOcean App Platform, Azure, or GCP.

### Local Docker Build & Test:
```bash
# Build the Docker image
docker build -t identra-ai:latest .

# Run container on port 5000
docker run -d -p 5000:5000 --name identra_container identra-ai:latest
```

Access local container at: `http://localhost:5000`

---

## 🪟 Option 4: Windows Production Service (Waitress)

To run Identra AI as a production server on Windows without Flask debug mode:

```powershell
# Activate Virtual Environment
.venv\Scripts\activate

# Launch Waitress WSGI Server
python -c "from waitress import serve; from app import create_app; serve(create_app(), host='0.0.0.0', port=5000)"
```

The production server will listen on `http://0.0.0.0:5000`.

---

## 🐧 Option 5: Linux VPS (Nginx + Gunicorn + Systemd)

For Ubuntu / Debian Linux Virtual Private Servers (DigitalOcean, Linode, AWS EC2, Vultr):

### 1. Install Dependencies & Tesseract OCR:
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv nginx tesseract-ocr
```

### 2. Clone & Setup Project:
```bash
cd /var/www
sudo git clone https://github.com/YOUR_USERNAME/Identra-AI.git
cd Identra-AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Create Systemd Service (`/etc/systemd/system/identra.service`):
```ini
[Unit]
Description=Identra AI Gunicorn Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/Identra-AI
ExecStart=/var/www/Identra-AI/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wsgi:app

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start identra
sudo systemctl enable identra
```

### 4. Configure Nginx (`/etc/nginx/sites-available/identra`):
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site & reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/identra /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ✅ Deployment Files Created in Repository:
- [`requirements.txt`](file:///C:/Users/KAMALIKA/.gemini/antigravity/scratch/MemoryVerse-AI/requirements.txt) - Contains Gunicorn & Waitress production servers
- [`wsgi.py`](file:///C:/Users/KAMALIKA/.gemini/antigravity/scratch/MemoryVerse-AI/wsgi.py) - WSGI production entry point
- [`Procfile`](file:///C:/Users/KAMALIKA/.gemini/antigravity/scratch/MemoryVerse-AI/Procfile) - Heroku / Render process declaration
- [`Dockerfile`](file:///C:/Users/KAMALIKA/.gemini/antigravity/scratch/MemoryVerse-AI/Dockerfile) - Multi-stage container setup with Tesseract OCR support
- [`.dockerignore`](file:///C:/Users/KAMALIKA/.gemini/antigravity/scratch/MemoryVerse-AI/.dockerignore) - Optimized Docker context filter
- [`render.yaml`](file:///C:/Users/KAMALIKA/.gemini/antigravity/scratch/MemoryVerse-AI/render.yaml) - Render 1-click cloud manifest
- [`.env.example`](file:///C:/Users/KAMALIKA/.gemini/antigravity/scratch/MemoryVerse-AI/.env.example) - Production environment template
