# 👕 AI Smart Wardrobe System

## 📌 Project Overview

The **AI Smart Wardrobe System** is a full-stack web application that integrates **computer vision, machine learning, and web development** to help users intelligently manage their clothing and receive outfit recommendations.

Users can upload clothing images, and the system will automatically:

* Recognize clothing category and attributes
* Store items in a personal wardrobe
* Recommend outfits based on current weather
* Find visually similar clothes using feature embeddings

This project is built using **Flask + PyTorch + Vue + SQLite**.

---

## 🚀 Features

### 👤 User System

* User registration and login
* Session-based authentication
* Multi-user data isolation (each user has an independent wardrobe)

---

### 🧥 Clothing Management

* Single upload & batch upload
* Automatic AI recognition:

  * Category (e.g., shirt, pants, coat)
  * Attributes (multi-label)
  * Main category (Tops / Pants / Shoes / etc.)
* Automatically generated tags:

  * Season (Spring/Summer, Autumn/Winter)
  * Thickness (Thin / Medium / Thick)
* Store feature vectors for similarity search
* View wardrobe with:

  * Sorting (Newest / Oldest)
  * Category filtering
  * Keyword search

---

### 🔍 Similarity Search

* Upload an image (not stored)
* Retrieve Top-K most similar clothes from wardrobe
* Based on **cosine similarity of deep features**

---

### 🌤 Weather-Based Recommendation

* Select city from dropdown
* Fetch real-time weather via API
* Recommend suitable clothes from wardrobe
* Scoring based on:

  * Temperature
  * Rain probability
  * Clothing thickness & season

---

### 🗑 Advanced Wardrobe Operations

* Delete single item
* Batch delete
* Recently deleted list
* Restore deleted items

---

### 🌐 Multi-Language Support

* Chinese
* English
* Spanish
* Japanese
* Korean

---

## 🧠 AI Model

* Backbone: **ResNet50**
* Multi-task learning:

  * Category classification (50 classes)
  * Attribute prediction (1000 classes)
* Feature extraction:

  * 2048-dim embedding
* Similarity:

  * Cosine similarity

---

## 🛠 Tech Stack

| Layer      | Technology           |
| ---------- | -------------------- |
| Frontend   | Vue 3 + HTML + CSS   |
| Backend    | Flask (Python)       |
| AI Model   | PyTorch              |
| Database   | SQLite               |
| Image Proc | PIL + torchvision    |
| API        | Open-Meteo (Weather) |

---

## 📂 Project Structure

```
smart-wardrobe/
│
├── backend.py
├── run.py
├── requirements.txt
│
├── app/
│   ├── __init__.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── auth.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── network.py
│   │   ├── labels.py
│   │   └── predictor.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── file_service.py
│   │   ├── clothes_service.py
│   │   ├── feature_service.py
│   │   └── weather_service.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── pages.py
│   │   ├── user_api.py
│   │   ├── wardrobe_api.py
│   │   ├── deleted_api.py
│   │   ├── dashboard_api.py
│   │   └── upload_api.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── constants.py
│       └── i18n.py
│
├── templates/
│   ├── index.html
│   ├── wardrobe.html
│   ├── login.html
│   ├── register.html
│   └── recent_deleted.html
│
├── static/
│   └── uploads/
│
├── dataset/
│   └── Anno_coarse/
│
└── checkpoint_c2_full_1000.pth
```

---

## ⚙️ Installation & Run

### 1️⃣ Clone project

```bash
git clone https://github.com/YOUR_USERNAME/smart-wardrobe.git
cd smart-wardrobe
```

---

### 2️⃣ Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

If missing:

```bash
pip install flask torch torchvision pillow numpy requests
```

---

### 4️⃣ Run backend

```bash
python backend.py
```

---

### 5️⃣ Open browser

```
http://127.0.0.1:5001
```

---

## 📌 Notes

* Model file (`.pth`) is not included due to size limitation
* Upload images are ignored by `.gitignore`
* SQLite database is auto-created

---

## 📈 Future Improvements

* Outfit combination recommendation
* UI/UX redesign
* Model optimization (faster inference)
* Deployment (Docker / Cloud)
* Mobile support

---

## 👤 Author

* Jingxuan Wang
* Computer Science Graduate Student
* University of Texas at Arlington

---

## ⭐ Highlights

* Full-stack AI system
* Real-time recommendation
* Multi-user support
* Multi-language UI
* Practical ML deployment

---

## 📷 Demo (Optional)

(Add screenshots here if needed)

---

## 📜 License

This project is for academic and educational purposes.
