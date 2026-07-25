# 🌱 Anganwadi Growth Monitoring System

A web-based child growth monitoring and nutrition management system designed to help Anganwadi workers efficiently manage child records, monitor growth, identify nutrition risks, and manage referrals.

---

## 📌 Project Overview

The Anganwadi Growth Monitoring System is a Flask-based web application that helps Anganwadi workers maintain digital records of children and monitor their health and nutritional growth.

The system provides a centralized dashboard to track registered children, growth measurements, nutrition status, alerts, referrals, and Anganwadi centre information.

It also includes an ML-based prediction module to assist in identifying children who may require referral.

---

## 🚀 Features

### 🔐 Authentication
- Admin Login
- Secure Session-based Authentication
- Logout Functionality
- Protected Application Routes

### 📊 Dashboard
- Total Registered Children
- Total Anganwadi Centres
- Open Referrals
- SAM Children Count
- MAM Children Count
- Normal Children Count
- Weight Loss Alerts

### 👶 Child Management
- Add New Child
- View Child Details
- Father and Mother Information
- Guardian Information
- Parent Contact
- Address
- Vaccination Status
- Centre Assignment
- Enrolment Date

### 📈 Growth Monitoring
- Add Growth Measurements
- Weight Tracking
- Height Tracking
- MUAC Tracking
- Measurement History
- Monthly Weight Gain
- Weight Growth Chart

### 🩺 Nutrition Monitoring
- Normal
- MAM (Moderate Acute Malnutrition)
- SAM (Severe Acute Malnutrition)
- WAZ Score Tracking

### 🚨 Growth Alerts
- Weight Loss Detection
- No Weight Gain Detection
- SAM Risk Detection

### 🚑 Referral Management
- Create Referrals
- View Open Referrals
- View Resolved Referrals
- Track Referral Reason
- Track Referral Outcome

### 🏫 Anganwadi Centre Management
- Add Anganwadi Centre
- View Centre Summary
- Centre-wise Child Listing
- Nutrition Status Summary

### 🤖 Machine Learning Prediction
- ML-based Referral Prediction
- Prediction Confidence Score
- Needs Referral Result
- No Referral Needed Result

---

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- Bootstrap
- JavaScript
- Bootstrap Icons
- Chart.js

### Backend
- Python
- Flask

### Database
- SQLite

### Machine Learning
- Python
- NumPy
- Pandas
- Scikit-learn
- Joblib

---

## 📂 Project Structure

```text
anganwadi-growth-monitor/
│
├── app.py
├── init_db.py
├── seed.sql
├── anganwadi.db
├── requirements.txt
├── README.md
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── index.html
│   ├── children.html
│   ├── add_child.html
│   ├── child_detail.html
│   ├── add_measurement.html
│   ├── alerts.html
│   ├── referrals.html
│   ├── add_referral.html
│   ├── centres.html
│   ├── add_centre.html
│   ├── centre_children.html
│   └── predict.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── ml/
    ├── train.py
    └── model.pkl