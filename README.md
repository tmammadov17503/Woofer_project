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

## Demo Path

Woofer is now easier to test in a pitch, partner meeting, or conference booth:

1. Open the live app.
2. Click **Load Luna sample profile** if you do not want to upload a dog photo yet.
3. Review the generated care plan, health tracker, vet-chat context, and Trust Passport export.
4. Open **Pilot Review** to mark partner evidence, save reviewer notes, and download a pilot report.

The sample profile uses the same app flow as a real uploaded-photo profile, so judges can evaluate the product experience, Trust Passport, and partner-review workflow even before they test image recognition.

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
5. **Trust Passport:** Country-aware readiness checklist for adoption, fostering, vet referral, or responsible transfer — without escrow or live-animal marketplace risk.
6. **Pilot Review:** No-auth partner review workflow for shelters, vets, fosters, and advisors to capture readiness status, notes, and next actions.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔬 **AI Breed Scanner** | MobileNetV2 neural network identifies dog breeds with confidence scoring |
| 📋 **Personalized Care Plans** | RAG-powered breed-specific nutrition, exercise, grooming & health guidance |
| 📄 **Care Guide PDFs** | Auto-generated printable care guides to share with vets or family |
| 🏥 **Health Tracker** | Track vet appointments, exercise goals, grooming schedules & health notes |
| ✅ **Trust Passport** | Market-aware transfer/adoption readiness document with missing-evidence guidance and PDF/Markdown export |
| 🧪 **Pilot Review** | Lightweight partner dashboard for readiness scores, reviewer notes, evidence gaps, and downloadable pilot reports |
| 🛒 **Smart Supply Finder** | Ethical affiliate links via Biopet.az, Wolt & Tap.az — no commission on animals |
| 🏠 **Adoption Resources** | Educational content promoting adoption; free access for shelters |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit app now; Vercel/Next.js migration planned after pilot validation |
| **AI / ML** | [TensorFlow CPU](https://www.tensorflow.org/) + [Keras](https://keras.io/) — MobileNetV2 |
| **RAG System** | Custom knowledge base with breed-specific care data |
| **Trust Layer** | Country-aware readiness profiles for Azerbaijan, Turkey, EU, and US expansion planning |
| **Language** | Python 3.9+ |
| **Database** | JSON by default, optional isolated MongoDB for pet profiles and pilot reviews |
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
│   ├── script.js
│   └── product-strategy.md      # Product strategy, Dosty differentiation & compliance plan
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

## Storage Options

Woofer runs with local JSON storage by default, so demos and local testing still work without any database setup.

For a private beta or partner pilot, enable a separate Woofer MongoDB database with Woofer-specific variables only:

```bash
WOOFER_STORAGE_BACKEND=mongodb
WOOFER_MONGODB_URI=<your Woofer-only MongoDB connection string>
WOOFER_MONGO_DB_NAME=woofer_private_beta
WOOFER_MONGO_COLLECTION=pet_profiles
```

Do not reuse generic `MONGODB_URI` values from other projects, trading bots, analytics services, or automation experiments. See [docs/storage-setup.md](docs/storage-setup.md) for the safe setup plan.

Or just use the **[live app](https://wooferproject.streamlit.app)** — no setup needed.

---

## ✅ Testing

Run the focused unit tests for the Trust Passport and storage logic:

```bash
python -m unittest discover -s tests -v
```

Run a syntax check for the app modules:

```bash
python -m py_compile Woofer/woofer_care_ai.py Woofer/trust_passport.py Woofer/storage.py Woofer/pilot.py
```

GitHub Actions also runs these checks on pushes and pull requests.

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
- Trust Passport for adoption, foster, vet referral, and responsible-transfer readiness
- No-auth Pilot Review workflow for early partner/advisor testing
- Educational content library

### 🔮 Future
- Custom domain (woofer.az)
- Regional expansion beyond Azerbaijan
- Vet telemedicine partnerships
- Country-by-country compliance profiles before any regulated transfer or payment feature
- Mobile app

---

## 🧭 Strategic Direction

Woofer is intentionally **not** starting as a live-animal marketplace or escrow product. Animal sales, breeder verification, ownership transfer, and payment custody are regulated differently across countries, so Woofer's first scalable wedge is the **trust and care-readiness layer**:

- help owners, adopters, shelters, and vets prepare better pet profiles;
- document care fit, vaccination/record readiness, owner consent, and follow-up plans;
- keep AI health guidance educational and transparent;
- defer escrow, listings, and breeder/payment flows until legal counsel and payment partners validate each market.

See [docs/product-strategy.md](docs/product-strategy.md) for the Dosty comparison, compliance response, and 30-day execution plan. See [docs/pilot-proposal.md](docs/pilot-proposal.md) for the partner pilot package, and [docs/vercel-migration-plan.md](docs/vercel-migration-plan.md) for the recommended frontend migration path.

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
