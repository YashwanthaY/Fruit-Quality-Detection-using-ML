# 🌿 FreshSense — AI Fruit Quality Detection System

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16-orange?style=flat-square&logo=tensorflow)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)
![Accuracy](https://img.shields.io/badge/Test%20Accuracy-95.9%25-brightgreen?style=flat-square)
![Languages](https://img.shields.io/badge/Languages-5-purple?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

> **Know Your Fruit. Protect Your Harvest.**
>
> A full-stack AI web application for real-time fruit quality detection using deep learning —
> built to help reduce post-harvest losses.

**🔗 Live Demo:** [freshsense-app.netlify.app](https://freshsense-app.netlify.app)
**🔗 API:** [fruit-quality-detection-using-ml-production.up.railway.app](https://fruit-quality-detection-using-ml-production.up.railway.app)

---

## 📸 Screenshots

### 🏠 Upload → Instant Result
![FreshSense homepage and detection result](screenshots/detection.png)

---

## 📌 Problem Statement

Post-harvest fruit losses cause significant economic damage to farmers and supply chains.
Manual quality inspection is slow, inconsistent, and expensive.
FreshSense uses a Convolutional Neural Network (CNN) to classify fruit quality in under a second —
helping farmers, food distributors, and quality inspectors make faster, more accurate decisions.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 AI Quality Detection | CNN (MobileNetV2, transfer learning) classifies fruit as Good / Intermediate / Bad |
| 📅 Shelf Life Estimation | Predicts remaining days of freshness |
| 🍏 Ripeness Score | Fresh-vs-rotten confidence ratio, scaled 5–98% |
| 🛡️ Storage Tips | Per-fruit expert storage and protection advice |
| 📊 Quality Score | Animated donut chart showing freshness percentage |
| 📈 Confidence Chart | Bar chart showing model certainty per class |
| ⚠️ Low-Confidence Disclaimer | Automatically flags any "bad" result under 50% model confidence for manual verification |
| 📋 Downloadable Report | Export full analysis to .txt file |
| ✏️ Manual Input Mode | Describe fruit by colour, texture, smell, age — no image needed |
| 🌍 5 Languages | English, Kannada, Hindi, Tamil, Telugu |
| 🌐 Multi-User Support | Stateless REST API supports unlimited concurrent users |
| 📱 Responsive Design | Works on desktop, tablet, and mobile |
| 🍎 8 Fruit Types | Apple, Banana, Grapes, Kiwi, Mango, Orange, Pear, Pineapple (fresh/rotten each — 16 classes total) |

---

## 🗂 Project Structure

```
Fruit-Quality-Detection/
│
├── frontend/                   ← Pure HTML / CSS / JS
│   ├── index.html              ← Complete single-page application
│   ├── style.css               ← Organic green + amber theme
│   ├── script.js               ← Upload, Chart.js, API calls
│   ├── translations.js         ← 5 language translations
│   └── lang.css                ← Language switcher styles
│
├── backend/                    ← Python Flask REST API
│   ├── app.py                  ← Flask routes (stateless, thread-safe)
│   ├── predict.py              ← AI prediction logic
│   ├── train_model.py          ← MobileNetV2 CNN training script
│   ├── requirements.txt        ← Python dependencies
│   ├── Procfile                ← Gunicorn start command (Railway)
│   └── model/
│       ├── fruit_saved_model/  ← Trained model (SavedModel format)
│       └── class_names.txt     ← 16 fruit class labels
│
├── dataset/
│   └── README.md               ← Dataset download instructions
│
├── screenshots/                ← README screenshots
│
└── README.md                   ← This file
```

---

## 🌐 Live Deployment

| Layer | Platform | URL |
|---|---|---|
| Frontend | Netlify | [freshsense-app.netlify.app](https://freshsense-app.netlify.app) |
| Backend API | Railway | [fruit-quality-detection-using-ml-production.up.railway.app](https://fruit-quality-detection-using-ml-production.up.railway.app) |

CORS on the backend is restricted to the Netlify origin only.

---

## 🚀 How to Run Locally

### Step 1 — Clone the repository
```bash
git clone https://github.com/YashwanthaY/Fruit-Quality-Detection-using-ML.git
cd Fruit-Quality-Detection-using-ML
```

### Step 2 — Create Python 3.11 virtual environment
```bash
cd backend
py -3.11 -m venv venv311
venv311\Scripts\activate        # Windows
# source venv311/bin/activate   # Mac/Linux
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Start Flask backend
```bash
python app.py
# → http://localhost:5000
```

### Step 5 — Start frontend server (new terminal)
```bash
cd ../frontend
python -m http.server 8080
```

### Step 6 — Open in browser
```
http://localhost:8080
```

> Note: `app.py` locally allows CORS from `*` only if you edit it back for local testing — the deployed version restricts origins to the Netlify domain. If running fully locally, point `frontend/script.js` at `http://localhost:5000` instead of the Railway URL.

---

## 🧠 Model Architecture

| Component | Detail |
|---|---|
| Base Model | MobileNetV2 (ImageNet pretrained) |
| Input Size | 224 × 224 × 3 |
| Head | GAP → BN → Dense(512) → Dense(256) → Softmax |
| Training | Phase 1: Head only · Phase 2: Fine-tune top 30 layers |
| Optimizer | Adam (Phase 1: 1e-3, Phase 2: 1e-5) |
| Epochs | 25 (EarlyStopping on val_accuracy) |
| Augmentation | Flip, Rotate, Zoom |
| Format | TensorFlow SavedModel (loaded via `TFSMLayer`, `call_endpoint="serve"`) |
| Training environment | Kaggle, dual T4 GPUs (`tf.distribute.MirroredStrategy`) |

---

## 📊 Model Accuracy

| Dataset | Result |
|---|---|
| Held-out test set (leak-free, 50 images/class) | **95.90%** |

An earlier version of this model reported 99.25% accuracy, but that number was invalid due to
train/test data leakage (test images were copies of training images). The dataset pipeline was
rebuilt with a genuine hold-out split, and 95.90% is the real, leak-free test accuracy.

---

## ⚠️ Known Limitations

Being upfront about where the model is weaker, rather than leaving it ambiguous:

- **`rottenpineapple` is 100% synthetic.** No public dataset of real rotten pineapple photos was
  available, so this class is trained on programmatically darkened fresh-pineapple images. Treat
  predictions for this class with caution.
- **`rottenkiwi` and `rottenpear` have very few real test photos** (9 and 15 respectively), sourced
  from a secondary Kaggle dataset. Training data for these classes is larger, but real-world test
  coverage is thin.
- **`freshmango`, `freshkiwi`, `freshpear`, and `freshpineapple`** have comparatively few real photos
  (36–50 each) versus 1,400+ for apple/banana/orange, so these classes rely more heavily on
  augmentation and may be less robust to unusual lighting or backgrounds.
- To compensate, the API flags any "bad" (rotten) prediction with **model confidence under 50%**
  with a disclaimer asking the user to verify visually — regardless of which fruit the model landed on.

---

## 🌐 API Endpoints

### `GET /health`
Health check.

### `POST /predict`
Upload a fruit image for AI analysis.

**Request:** `multipart/form-data` — key = `image`

**Response:**
```json
{
  "quality_label":        "good",
  "quality_percentage":   98,
  "ripeness_label":       "Peak Freshness",
  "confidence_score":     98,
  "shelf_life_days":      "7-10 Days",
  "storage_tips":         ["Store in fridge crisper drawer", "..."],
  "fruit_type":           "Apple",
  "recommendation":       "Safe for immediate consumption.",
  "confidence_breakdown": { "good": 98, "intermediate": 1, "bad": 1 },
  "disclaimer":           null,
  "analysis_time_seconds": 0.02
}
```

### `POST /predict-manual`
Describe fruit attributes as JSON — no image required.

**Request:**
```json
{
  "fruit_type": "apple",
  "color": "vibrant",
  "texture": "firm",
  "smell": "fresh",
  "days_since_harvest": 3
}
```

---

## 🔄 Multi-User Architecture

FreshSense is designed for unlimited concurrent users:

- Each HTTP request runs in its **own thread**
- **No shared mutable state** between requests
- Uploaded images saved to **unique temp files** (UUID-named) and deleted after prediction
- ML model loaded **once at startup** — read-only during inference (thread-safe)
- Production runs on **Gunicorn** (`gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`) via Railway

---

## 🌍 Supported Languages

| Language | Script | Status |
|---|---|---|
| English | Latin | ✅ Complete |
| ಕನ್ನಡ Kannada | Kannada | ✅ Complete |
| हिंदी Hindi | Devanagari | ✅ Complete |
| தமிழ் Tamil | Tamil | ✅ Complete |
| తెలుగు Telugu | Telugu | ✅ Complete |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JS, Chart.js 4 — deployed on Netlify |
| Backend | Python 3.11, Flask 3.0, Flask-CORS, Gunicorn — deployed on Railway |
| ML Model | TensorFlow 2.16, Keras, MobileNetV2 transfer learning |
| Dataset | Fruits Fresh & Rotten (Kaggle) + a secondary Kaggle dataset for kiwi/pear rotten photos |
| Training | Kaggle Notebooks, dual T4 GPUs |

---

## 📦 Dataset

**Primary Dataset:** Fresh and Rotten Fruits — Kaggle
https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification

**Secondary Dataset (real rotten kiwi/pear photos):**
https://www.kaggle.com/datasets/nourabdoun/fruits-quality-fresh-vs-rotten

See `dataset/README.md` for full download instructions.

**Training notebook:** https://www.kaggle.com/code/yashwanthagastya12/fruit-quality-detection-ml

---

## 🔮 Roadmap

- [x] Deploy online with live URL (Netlify + Railway)
- [x] Fix confidence-based low-confidence disclaimer
- [x] Lock down CORS to production frontend only
- [ ] Price suggestion engine — Grade A/B/C market pricing
- [ ] Three user modes: farmer / market / home
- [ ] Mobile app (Android/iOS) for field use
- [ ] Disease detection (not just freshness)
- [ ] Real-time webcam analysis
- [ ] User accounts and history tracking

---

## 👤 Author

**Yashwantha Y**
Student — Computer Science (AI/ML)

📧 yashwanthagastya12@gmail.com
🔗 [LinkedIn](https://linkedin.com/in/your-profile)
💻 [GitHub](https://github.com/YashwanthaY)

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- Dataset by **sriramr** and **nourabdoun** on Kaggle
- MobileNetV2 architecture by Google
- Trained on Kaggle Notebooks (free dual T4 GPUs)