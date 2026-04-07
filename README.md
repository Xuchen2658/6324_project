# 🧠 AI Smart Wardrobe System

An intelligent wardrobe system built with **Flask + PyTorch + YOLO + multi-model fusion**, designed to provide:

* Clothing recognition (category + attributes + color)
* Wardrobe management (filtering / search / sorting)
* Weather-aware recommendations
* Occasion-based recommendations
* Intelligent outfit generation
* Full Chinese / English interface switching

---

# 🚀 Key Features

## 1. Dual-Model Fusion

The system uses **two models collaboratively**:

| Model                       | Responsibility                                              |
| --------------------------- | ----------------------------------------------------------- |
| Legacy Model (ResNet50)     | Stable clothing category classification + feature embedding |
| New Model (YOLO + ConvNeXt) | Color detection + fine-grained attribute prediction         |

### Benefits

* Stable clothing categories
* Richer attributes
* Better color recognition
* Preserves similarity search performance

---

## 2. Clothing Recognition

Each uploaded clothing item is automatically analyzed and stored with:

* `category_name`
* `main_category`
* `attribute_names`
* `color_name`
* `season`
* `thickness`
* `feature`

The system supports both:

* Single image upload
* Multiple image upload

---

## 3. Advanced Color Detection

The updated color recognition module includes:

* YOLO-based segmentation
* HSV color analysis
* Multi-region color detection
* Skin filtering
* Extended hue coverage across the color wheel
* Better distinction among beige, white, brown, pink, and red

---

## 4. Weather-Aware Recommendation

The system uses weather data to recommend suitable clothes based on:

* Current temperature
* Apparent temperature
* Daily maximum and minimum temperature
* Rain probability

### Supported display features

* Celsius / Fahrenheit conversion button
* Dynamic temperature display switching in the weather module

---

## 5. Occasion-Based Recommendation

Supported occasions:

* Daily
* Work
* Sport
* Party
* Formal
* Travel
* Home

Each item is scored according to:

* Occasion matching
* Clothing category
* Clothing role
* Weather suitability
* Thickness / season compatibility

---

## 6. Intelligent Outfit Recommendation

The system automatically generates outfit combinations such as:

```text
Top + Bottom
Dress
Top + Bottom + Outerwear
```

### Rule-based outfit logic includes:

* Role grouping (`Top`, `Bottom`, `Dress`, `Outerwear`, `Shoes`)
* Occasion scoring
* Color harmony rules
* Temperature / layering rules
* Cloth type constraints (`single_piece` / `two_piece`)
* Conflict penalties for unsuitable combinations

---

## 7. Full Bilingual Interface

The system now supports **fully synchronized Chinese and English display**.

### This includes:

* UI labels
* Clothing category names
* Main categories
* Roles
* Attributes
* Color names
* Occasion names
* Recommendation reasons

### Result

* Chinese page displays all content in Chinese
* English page displays all content in English

---

## 8. Weather Cache Optimization

To reduce repeated API requests and prevent timeout errors:

* Weather is cached for 10 minutes per city
* Cached results are reused for repeated recommendations
* Fallback to old cached data when API fails

### Fixes

* 502 Bad Gateway errors
* Timeout issues
* Slow recommendation refresh

---

# 🧩 System Features

## User System

* Register
* Login
* Logout
* Multi-user isolation

## Clothing Management

* Single upload
* Batch upload
* Delete
* Batch delete
* Recently deleted
* Restore deleted items

## Wardrobe Features

* View all clothes
* Category filtering
* Keyword search
* Sort by newest / oldest

## Recommendation Features

* Weather-aware recommendation
* Occasion-based recommendation
* Intelligent outfit recommendation

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
├── static/
│   ├── js/
│   ├── css/
│   └── uploads/
│
├── dataset/Anno_coarse/
│
├── checkpoint_c2_full_1000.pth
├── model0405.pth
├── yolov8n-seg.pt
└── backfill_occasion_role.py
```

---

# ⚙️ Installation & Setup

## 1. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
pip install ultralytics opencv-python scikit-learn
```

## 3. Run the project

```bash
python backend.py
```

## 4. Open in browser

```text
http://127.0.0.1:5000
```

---

# 🧠 Recommendation Logic

## Item Recommendation

Each clothing item is scored based on:

* Occasion match
* Category suitability
* Weather compatibility
* Season and thickness match

## Outfit Recommendation

Outfits are generated using rule-based templates and ranking:

* Top + Bottom
* Dress
* Top + Bottom + Outerwear

Additional scoring includes:

* Color compatibility
* Layering suitability
* Cloth type consistency
* Occasion conflict penalties

---

# 🌐 Language Support

The system supports both:

* Chinese
* English

All displayed content is translated consistently, including recommendation reasons.

---

# 🌡 Temperature Unit Switch

The weather module supports:

* Celsius (°C)
* Fahrenheit (°F)

Users can switch units directly from the homepage weather panel without changing backend data.

---

# ⚠️ Common Issues

## Recommendation score is 0

Run:

```bash
python backfill_occasion_role.py
```

This restores:

* `occasion_tags`
* `role`

## Weather API timeout or 502 error

The system now uses:

* correct weather API parameters
* request timeout control
* 10-minute cache fallback

## Wrong category prediction

The system solves this by:

* using the legacy model for category classification
* using the new model only for color and detailed attributes

---

# 📌 Future Improvements

* Saved outfit collections
* User preference learning
* Explainable recommendation details
* More fine-grained fashion style classification
* More language options

---

# 🧾 Tech Stack

* Flask
* PyTorch
* YOLOv8
* ConvNeXt
* OpenCV
* SQLite
* Vue

---

# 👨‍💻 Author

UTA CSE Project
AI Smart Wardrobe System
