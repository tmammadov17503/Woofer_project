# 🐕 Woofer Care AI: Intelligent Pet Analysis & Welfare Platform

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Streamlit-FF4B4B)](https://streamlit.io/)
[![AI Model](https://img.shields.io/badge/AI-MobileNetV2-green)](https://keras.io/api/applications/mobilenet/)
[![Ethics](https://img.shields.io/badge/Ethics-Adoption%20First-orange)](https://wooferproject.streamlit.app)
[![Live App](https://img.shields.io/badge/Live%20App-Streamlit-FF4B4B?logo=streamlit)](https://wooferproject.streamlit.app)
[![Website](https://img.shields.io/badge/Website-GitHub%20Pages-222?logo=github)](https://tmammadov17503.github.io/Woofer_project/)

**Woofer Care AI** is an ethical, AI-powered platform that promotes responsible pet ownership through intelligent dog breed analysis and personalized care recommendations. By combining **Computer Vision** with **Retrieval-Augmented Generation (RAG)**, Woofer empowers pet owners — especially adopters — with the knowledge they need to provide optimal care for their companions.

> 🚫 **Ethical Commitment:** Woofer does not support, facilitate, or promote the buying, selling, or breeding of animals. We are dedicated to adoption support, welfare education, and responsible ownership.

---

## 🔗 Links

| | |
|---|---|
| 🚀 **Live App** | [wooferproject.streamlit.app](https://wooferproject.streamlit.app) |
| 🌐 **Website** | [tmammadov17503.github.io/Woofer_project](https://tmammadov17503.github.io/Woofer_project/) |
| 🎬 **Demo Video** | [Watch on YouTube](https://youtu.be/u8eg741j8n8) |
| 📄 **Presentation** | [Woofer_presentation.pdf](./Woofer_presentation.pdf) |

---

## 🎯 Mission & Vision

### The Problem
- **Information Gap:** New pet owners, especially adopters, often lack breed-specific knowledge to provide proper care.
- **Health Risks:** Misunderstanding dietary, exercise, and grooming needs leads to preventable health issues.
- **Abandonment:** Lack of preparation and support contributes to pets being returned to shelters.
- **Unethical Markets:** Many platforms profit from pet sales, perpetuating puppy mills and irresponsible breeding.

### The Woofer Solution
1. **AI Breed Analysis:** Instant identification of breed characteristics to understand specific care needs.
2. **Personalized Care Guides:** RAG-powered recommendations for nutrition, exercise, grooming, and health monitoring.
3. **Health Tracking:** Tools to monitor vet appointments, exercise goals, and wellness milestones.
4. **Adoption Support:** Resources and education to promote successful adoptions and reduce returns.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔬 **AI Breed Scanner** | MobileNetV2 neural network identifies dog breeds with confidence scoring |
| 📋 **Personalized Care Plans** | RAG-powered breed-specific nutrition, exercise, grooming & health guidance |
| 📄 **Care Guide PDFs** | Auto-generated printable care guides to share with vets or family |
| 🏥 **Health Tracker** | Track vet appointments, exercise goals, grooming schedules & health notes |
| 🛒 **Smart Supply Finder** | Ethical affiliate links via Biopet.az, Wolt & Tap.az — no commission on animals |
| 🏠 **Adoption Resources** | Educational content promoting adoption; free access for shelters |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | [Streamlit](https://streamlit.io/) |
| **AI / ML** | [TensorFlow CPU](https://www.tensorflow.org/) + [Keras](https://keras.io/) — MobileNetV2 |
| **RAG System** | Custom knowledge base with breed-specific care data |
| **Language** | Python 3.9+ |
| **Database** | JSON (persistent pet profiles & health records) |
| **PDF Generation** | [FPDF2](https://py-fpdf2.readthedocs.io/) |
| **Deployment** | [Streamlit Community Cloud](https://streamlit.io/cloud) |
| **Website** | GitHub Pages (HTML/CSS/JS) |

---

## 📁 Repository Structure

```
Woofer_project/
├── Woofer/
│   └── woofer_care_ai.py      # Main Streamlit application
├── docs/                       # GitHub Pages website
│   ├── index.html
│   ├── style.css
│   └── script.js
├── requirements.txt            # Python dependencies
├── Woofer_presentation.pdf     # Project presentation
└── README.md
```

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/tmammadov17503/Woofer_project
cd Woofer_project
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the app:**
```bash
streamlit run Woofer/woofer_care_ai.py
```

Or just use the **[live app](https://wooferproject.streamlit.app)** — no setup needed.

---

## 🐾 How It Works

**Step 1 — Upload a photo**
Upload any clear photo of your dog. The AI analyzes breed characteristics with confidence scoring in seconds.

**Step 2 — Get your care plan**
Receive instant breed-specific guidance on:
- **Nutrition:** Diet type, calorie needs, feeding schedules, foods to avoid
- **Exercise:** Daily requirements, recommended activities, mental stimulation
- **Grooming:** Brushing frequency, bathing schedules, special care needs
- **Health:** Common issues to monitor, vet checkup schedules, lifespan expectations

**Step 3 — Track & thrive**
- Download a personalized PDF care guide
- Track health milestones and vet appointments
- Find supplies through ethical affiliate partners (Biopet.az, Wolt, Tap.az)

---

## 💰 Ethical Business Model

Woofer operates on a sustainable revenue model that **never involves transactions for live animals**:

| Plan | Price | Features |
|---|---|---|
| 🐾 **Free** | 0 AZN / forever | AI breed analysis, basic care recommendations, single pet profile |
| ⭐ **Basic** | 4.99 AZN / mo | Advanced health tracking, multiple pet profiles, priority support |
| 🚀 **Pro** | 9.99 AZN / mo | Vet integration, detailed analytics, custom care plans |
| 🏠 **Shelters** | Free | Full premium access for registered rescue organizations |

**Ethical Affiliate Marketing:** Commission on pet supplies only — we never earn from pet sales.

---

## 🗺️ Roadmap

### ✅ Phase 1 — Foundation (Q2 2025)
- AI breed analysis engine with MobileNetV2
- RAG-based care recommendation system
- Integration with Azerbaijani e-commerce platforms
- Deployed live on Streamlit Cloud

### ✅ Phase 2 — Launch (Q3 2025)
- Public app live at [wooferproject.streamlit.app](https://wooferproject.streamlit.app)
- Landing website at [GitHub Pages](https://tmammadov17503.github.io/Woofer_project/)
- Demo video published

### 🔄 Phase 3 — Welfare Network (Q4 2025)
- Veterinary clinic integration & appointment booking
- Foster coordination tools for shelters
- Educational content library

### 🔮 Future
- Custom domain (woofer.az)
- Regional expansion beyond Azerbaijan
- Vet telemedicine partnerships
- Mobile app

---

## 🛡️ Ethical Guidelines

1. **No Live Animal Sales** — We never facilitate, promote, or profit from the sale of animals.
2. **Adoption First** — We prioritize and promote adoption over purchasing.
3. **Welfare Over Profit** — Revenue models never incentivize animal breeding or sales.
4. **Education** — We provide resources to combat misinformation about pet care.
5. **Transparency** — AI recommendations never replace veterinary advice.

---

## 🤝 Partnerships

We actively seek partnerships with:
- **Animal Shelters & Rescues** — Free premium access for all registered organizations
- **Veterinary Clinics** — Integration and referral partnerships
- **Pet Supply Retailers** — Ethical affiliate relationships (Biopet.az, Wolt, Tap.az)
- **Welfare Organizations** — Collaboration on education and adoption initiatives

---

## 📝 License

This project is open-source and available for use by animal welfare organizations, shelters, and individual pet owners. Commercial use that violates our ethical guidelines (facilitating pet sales, supporting puppy mills, etc.) is strictly prohibited.

---

**Woofer Care AI** — *Promoting Responsible Pet Ownership Through Technology*

© 2025 Woofer Project | Made with ❤️ for animals everywhere | Azerbaijan 🇦🇿
