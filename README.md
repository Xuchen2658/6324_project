# 🧠 AI Smart Wardrobe System

A **Flask + PyTorch + YOLO + multi-model fusion** based intelligent wardrobe system that provides:

* 👕 Clothing recognition (category + attributes + color)
* 📊 Wardrobe management (filter / search / sorting)
* 🌦 Weather-aware recommendations
* 🎯 Occasion-based recommendations (Work / Travel / Sport, etc.)
* 👗 Intelligent outfit generation (Top + Bottom / Dress / Layered outfits)

---

# 🚀 Key Features

## 🧠 Dual-Model Fusion (Core Architecture)

This system uses **two models collaboratively**:

| Model                         | Responsibility                                       |
| ----------------------------- | ---------------------------------------------------- |
| ✅ Legacy Model (ResNet50)     | Clothing category classification + feature embedding |
| ✅ New Model (YOLO + ConvNeXt) | Color detection + fine-grained attributes            |

### Benefits:

* Stable category prediction (no more incorrect outputs like *“Sateen”*)
* Rich attribute understanding (color, pattern, sleeve type, etc.)

---

## 🎨 Advanced Color Detection

* YOLO-based human segmentation
* HSV color space analysis
* Multi-region detection (upper/lower body)
* KMeans color feature extraction

### Improvements:

* ✅ Better beige vs white distinction
* ✅ Reduced red vs pink confusion
* ✅ Skin-color interference removed

---

## 👗 Intelligent Outfit Recommendation

Automatically generates outfit combinations:

```text
Top + Bottom
Dress
Top + Bottom + Outerwear
```

### Supports:

* Layered outfits
* Single-piece outfits
* Daily practical combinations

---

## 🎯 Occasion-Based Recommendation

Supported occasions:

* Daily
* Work
* Sport
* Party
* Formal
* Travel
* Home

### Logic:

* Matches `occasion_tags`
* Uses clothing `role` (Top / Bottom / Dress / Outerwear)
* Category keyword-based scoring

---

## 🌦 Weather-Aware Recommendation

Powered by Open-Meteo API:

* Temperature
* Apparent temperature
* Precipitation probability

### Behavior:

* Cold → recommend thick clothing
* Hot → recommend light clothing
* Rain → recommend outerwear / dark colors

---

## ⚡ Weather Cache Optimization

* Weather is cached for **10 minutes per city**
* Prevents excessive API calls

### Fixes:

* ❌ 502 errors
* ❌ Timeout issues
* ❌ Slow response

---

# 🧩 System Features

## 👤 User System

* Register / Login / Logout
* Multi-user isolation

---

## 👕 Clothing Management

* Single upload
* Batch upload
* Batch delete
* Recently deleted (Recycle Bin)
* Restore items

---

## 🧥 Wardrobe Features

* View all items
* Category filtering (Tops / Pants / Skirts / Shoes, etc.)
* Keyword search
* Sorting (Newest / Oldest)

---

## 🤖 AI Recognition Output

Each clothing item includes:

* `category_name`
* `main_category`
* `attribute_names`
* `color_name`
* `season`
* `thickness`
* `feature` (for similarity search)

---

## 👗 Recommendation Fields

Additional attributes for recommendation:

* `occasion_tags`
* `role` (Top / Bottom / Dress / Outerwear / Shoes)
* `cloth_type` (single / two_piece)

---

# 📁 Project Structure

```text
smart-wardrobe/
│
├── backend.py
├── README.md
├── requirements.txt
│
├── app/
│   ├── models/
│   │   ├── legacy_predictor.py
│   │   ├── attr_predictor.py
│   │   └── predictor.py
│   │
│   ├── services/
│   │   ├── clothes_service.py
│   │   └── weather_service.py
│   │
│   ├── routes/
│   │   ├── upload_api.py
│   │   ├── dashboard_api.py
│   │   └── deleted_api.py
│
├── templates/
├── static/uploads/
├── dataset/Anno_coarse/
│
├── checkpoint_c2_full_1000.pth
├── model0405.pth
├── yolov8n-seg.pt
```

---

# ⚙️ Installation & Setup

## 1️⃣ Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
pip install ultralytics opencv-python scikit-learn
```

---

## 3️⃣ Run the Application

```bash
python backend.py
```

---

## 4️⃣ Open in Browser

```text
http://127.0.0.1:5000
```

---

# 🧠 Recommendation System

## Item Scoring

Based on:

* Occasion matching (+4)
* Category rules (+1~3)
* Weather compatibility (+2~3)

---

## Outfit Generation

Steps:

1. Group items by `role`
2. Rank by score
3. Generate combinations:

```text
Top + Bottom
Dress
Top + Bottom + Outerwear
```

---

# ⚠️ Troubleshooting

## ❌ Recommendation score = 0

Cause:

* Missing `occasion_tags` or `role`

Fix:

```bash
python backfill_occasion_role.py
```

---

## ❌ Weather API errors

Fixed:

* Parameter issues
* Excessive requests
* Timeout handling

---

## ❌ Wrong category prediction

Solution:

* Legacy model handles classification
* New model only handles attributes

---

# 📌 Future Improvements

* Outfit similarity recommendation
* Save outfit combinations
* User preference learning
* Explainable recommendation
* Multi-language UI (EN / CN / JP / KR)

---

# 🧾 Tech Stack

* Flask
* PyTorch
* YOLOv8
* ConvNeXt
* OpenCV
* SQLite
* Vue (Frontend)

---

# 👨‍💻 Author

UTA CSE Project
AI Smart Wardrobe System
