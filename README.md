# SafeHer – Women Safety Monitoring System

SafeHer is a full-stack women safety web application designed to provide real-time emergency assistance through live GPS tracking, geo-fencing, panic alerts, fall detection, and SMS notifications to trusted contacts.

---

## 🚀 Features

### 📍 Location Tracking
- Live GPS tracking using browser geolocation
- Interactive map display using Leaflet
- "Show Current Location" button to fetch coordinates

### 🛡️ Safety Features
- Emergency Panic Button
- Fall Detection Simulation
- Geo-fencing with customizable center and radius
- Automatic alerts when the user exits the safe zone

### 👤 User Management
- User registration and login
- Contact management for Parent, Guardian, and Warden
- Alerts sent only to contacts linked to the logged-in user

### 📩 SMS Notifications
- Simulated SMS alerts via backend console
- Optional real SMS delivery using Twilio API

### ⚙️ Additional Features
- Automatic MySQL database and table creation
- Light/Dark mode toggle

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript
- Leaflet.js

### Backend
- Python
- Flask

### Database
- MySQL

### External Services
- Twilio API 

---

## 📸 Screenshots

<img width="1920" height="1200" alt="Screenshot 2026-03-28 112649" src="https://github.com/user-attachments/assets/11b3a1a6-eabb-49c7-b391-a6063bc56bf2" />

<img width="1920" height="1200" alt="Screenshot 2026-03-28 113200" src="https://github.com/user-attachments/assets/5128b165-e579-4edf-9f66-be20c35cc9f8" />

<img width="1920" height="1200" alt="Screenshot 2026-03-28 113233" src="https://github.com/user-attachments/assets/27007451-73aa-4766-982b-fdd9e0c3aa10" />

<img width="1920" height="1200" alt="Screenshot 2026-03-28 113315" src="https://github.com/user-attachments/assets/443a69f4-b06f-419e-9e5c-85cc0ae0519d" />

<img width="1920" height="1200" alt="Screenshot 2026-03-28 113503" src="https://github.com/user-attachments/assets/999f1823-59b1-4f5d-a8f5-bc0d4555703d" />

<img width="1920" height="1200" alt="Screenshot 2026-03-28 113546" src="https://github.com/user-attachments/assets/87e06ae4-aa73-46c0-9aa5-fb3709603416" />

<img width="1920" height="1200" alt="Screenshot 2026-03-28 113708" src="https://github.com/user-attachments/assets/f3f4aeac-0cd7-4b5e-943f-8ac9b2c98d98" />


---

## 📂 Project Structure

```bash
SafeHer/
├── backend/
├── static/
├── templates/
├── screenshots/
├── requirements.txt
└── README.md
```

---

## ⚙️ Run the Project

```powershell
cd C:\Users\Admin\OneDrive\Desktop\miniproject\women_safety_system
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd backend
python app.py
```

Open in browser:

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/register-page`

---

## 📱 Real SMS with Twilio (Optional)

Set environment variables:

```powershell
$env:SMS_PROVIDER="twilio"
$env:TWILIO_ACCOUNT_SID="ACxxxxxxxx"
$env:TWILIO_AUTH_TOKEN="xxxxxxxx"
$env:TWILIO_FROM_NUMBER="+1xxxxxxxxxx"
```

---

## 🗄️ MySQL Configuration

Configured in `backend/config.py`:

- Host: `xxx`
- User: `xxx`
- Password: `xxx`
- Database: `women_safety_db`



