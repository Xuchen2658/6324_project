# 👕 Intelligent Clothing Management System

## 📌 Project Overview

This project is an intelligent clothing management system based on computer vision.
It uses a deep learning model (ResNet-50) to automatically recognize clothing categories and attributes from images, and provides similarity retrieval and recommendation functions.

---

## 🚀 Features

### 1. Clothing Image Recognition

* Upload clothing images
* Automatically identify:

  * Category (e.g., hoodie, shirt)
  * Attributes (e.g., black, long-sleeve)
* Display results on web interface

### 2. Feature Extraction

* Extract 2048-dimensional feature vectors using CNN
* Save feature vectors locally (`.npy` files)

### 3. Similar Clothing Retrieval

* Compare feature vectors using cosine similarity
* Retrieve top-K similar clothing items

### 4. Recommendation System

* Provide simple rule-based recommendations
* Based on category and attributes

---

## 🏗️ Tech Stack

* Python 3.10+
* Flask (Backend)
* Vue 3 + Element Plus (Frontend)
* PyTorch (Deep Learning)
* NumPy (Feature processing)

---

## 📂 Project Structure

6324_project/\
│\
├── backend.py\
├── checkpoint_c2_full_1000.pth\
├── dataset/\
│└── Anno_coarse/\
│\
├── templates/\
│   └── index.html\
│\
├── static/\
│   └── uploads/\
│\
└── requirements.txt

---

## ⚙️ Installation & Setup

### 1. Clone the repository

git clone https://github.com/your-username/your-repo.git
cd your-repo

### 2. Create virtual environment

python3 -m venv .venv
source .venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

---

## ▶️ Run the Project

python backend.py

Then open browser:
http://127.0.0.1:5001

---

## 📸 Usage

1. Upload an image of clothing
2. System will:

   * Identify category & attributes
   * Show similar clothing
   * Provide recommendations

---

## 📌 Notes

* First upload may be slower due to model loading
* Similar items appear after multiple uploads
* All uploaded images are stored in `static/uploads`

---

## 👥 Team Members

* Jingxuan Wang
* Xuchen Wang

---

## 🎯 Future Work

* Integrate weather API for smart recommendations
* Add database for clothing storage
* Improve recommendation algorithm
* Optimize model performance
