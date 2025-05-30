# 🚘 SmartAccess: License Plate Detection System

SmartAccess is an AI-powered license plate recognition system designed for **residential apartment complexes** to automatically identify and log vehicle entries. Built using Python, Flask, EasyOCR, and SQLite, it ensures **secure access** and provides a real-time **admin dashboard** to manage user and detection records.

---

## 🔧 Features

- **Admin login portal**
- **User registration form** (name, mobile, car number, email, flat number)
- **Image upload** and license plate detection using EasyOCR
- **Plate match verification** with registered users
- **Detection history** and daily statistics
- **Hugging Face OCR** integrated for plate detection (Gradio/Glitch support)
- **Tracks how many times a plate is detected per day**
- SQLite database with two tables: `users`, `detections`

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python (Flask)** | Backend server & API |
| **SQLite** | Lightweight database |
| **HTML + Bootstrap 5** | Frontend UI |
| **EasyOCR + OpenCV** | License plate detection |
| **Gradio (Hugging Face)** | Web OCR interface |
| **Glitch.com** | Hosting Flask backend |

---

## 📂 Database Schema

### `users`
| Field       | Type     |
|-------------|----------|
| id          | INTEGER PRIMARY KEY AUTOINCREMENT |
| name        | TEXT     |
| mobile      | TEXT     |
| car_number  | TEXT UNIQUE |
| email       | TEXT     |
| flat_number | TEXT     |

### `detections`
| Field       | Type     |
|-------------|----------|
| tid         | INTEGER PRIMARY KEY AUTOINCREMENT |
| car_number  | TEXT     |
| name        | TEXT     |
| timestamp   | TEXT (DateTime) |

---

## 🧭 Project Flow

1. User submits registration form
2. Admin logs into the dashboard
3. Admin uploads an image → EasyOCR extracts license plate
4. If plate matches, name and flat are shown and stored in `detections`
5. If unmatched, name is marked as **Unknown**
6. Admin views records and stats on dashboard

---

## 🚀 How to Run Locally

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/smartaccess.git
   cd smartaccess
