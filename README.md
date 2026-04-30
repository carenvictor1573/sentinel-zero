# Sentinel Zero

# 🚨 Sentinel Zero – AWS Security Monitoring System

A real-time cloud security monitoring system built on AWS that detects anomalous user behavior, generates alerts, and visualizes threats through an interactive dashboard.

---

## 🧠 Project Overview

Sentinel Zero simulates a **Security Operations Center (SOC)** environment by continuously monitoring AWS activity logs, identifying suspicious patterns, and presenting insights through a live dashboard.

The system is designed to detect:
- Unusual login locations  
- High-frequency activity  
- Suspicious API usage patterns  

---

## 🏗️ Architecture

CloudTrail 
   ↓
EventBridge 
   ↓
Lambda (Detection Logic)
   ↓
DynamoDB (Storage)
   ↓
SNS (Email Alerts)
   ↓
Streamlit Dashboard (Visualization)


---

## ⚙️ Key Features

### 🔍 Threat Detection
- Detects **new IP access**
- Identifies **high-frequency activity**
- Flags **multiple anomaly signals**
- Assigns **severity levels (HIGH / MEDIUM / LOW)**

---

### 🚨 Alerting System
- Real-time alerts triggered via Lambda
- Email notifications using SNS
- Risk-based classification of threats

---

### 📦 Data Storage
- DynamoDB stores:
  - User behavior history  
  - Alert logs  

---

### 📊 Interactive Dashboard
- Live AWS-connected dashboard
- Filter alerts by severity
- View suspicious activity patterns

---

### 🌍 Attacker Intelligence
- Converts IP → **Country**
- Helps identify attacker origin

---

### 🔐 Secure Access
- Login-protected dashboard
- Simulates role-based access control

---

## 🖥️ Dashboard Preview

### 🔐 Login Page
![Login](docs/images/login.png)

---

### 📊 Main Dashboard
![Dashboard](docs/images/dashboard.png)

---

### 📄 Alert Data
![Alerts](docs/images/alerts.png)

---

### 🌍 Top Suspicious IPs
![Top IPs](docs/images/top_ips.png)

---

### 📈 Activity Timeline
![Timeline](docs/images/timeline.png)

---

## ☁️ AWS Components

### 📦 DynamoDB Tables
![DynamoDB](docs/images/dynamodb.png)

---

### ⚡ Lambda Function
![Lambda](docs/images/lambda.png)

---

### 🔁 EventBridge Rule
![EventBridge](docs/images/eventbridge.png)

---

## 🛠️ Tech Stack

- **AWS Services**
  - Lambda  
  - DynamoDB  
  - EventBridge  
  - SNS  
  - CloudTrail  

- **Backend**
  - Python (Boto3)

- **Frontend**
  - Streamlit  

- **Data Processing**
  - Pandas  

---

## ▶️ Running the Dashboard

```bash
python -m streamlit run dashboard/dashboard_app.py
```

## Project Structure

sentinel-zero/
│
├── dashboard/
│   └── dashboard_app.py
│
├── lambda/
│   └── lambda_function.py
│
├── docs/
│   └── images/
│
├── requirements.txt
├── README.md
└── .gitignore

## 🚀 Future Enhancements
🌍 Geo-mapping visualization (map-based attacks)

🔐 Integration with AWS IAM / Cognito for real authentication

📊 Advanced analytics (trend prediction)

🚨 Slack / webhook alert integration

🧠 Machine learning–based anomaly detection

## 👥 Contributors
Caren Victor and J Aesu Keerthana

