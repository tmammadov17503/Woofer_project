import streamlit as st
import numpy as np
from PIL import Image
import time
import json
import os
from datetime import datetime, timedelta
from fpdf import FPDF
import re
import urllib.parse
import requests

try:
    from Woofer.trust_passport import (
        COMPLIANCE_MARKETS,
        TRUST_PASSPORT_CHECKS,
        build_trust_passport_pdf,
        build_trust_passport,
        calculate_readiness_score,
        get_missing_readiness_checks,
    )
    from Woofer.storage import (
        StorageConfigurationError,
        create_pet_profile_repository,
    )
except ImportError:
    from trust_passport import (
        COMPLIANCE_MARKETS,
        TRUST_PASSPORT_CHECKS,
        build_trust_passport_pdf,
        build_trust_passport,
        calculate_readiness_score,
        get_missing_readiness_checks,
    )
    from storage import (
        StorageConfigurationError,
        create_pet_profile_repository,
    )

# ── Tensorflow / Keras ────────────────────────────────────────────────────────
try:
    import tensorflow as tf
    try:
        from keras.applications.mobilenet_v2 import (
            MobileNetV2, preprocess_input, decode_predictions,
        )
        from keras.utils import load_img, img_to_array as _img_to_array

        class keras_image:
            @staticmethod
            def load_img(path, target_size=None):
                return load_img(path, target_size=target_size)
            @staticmethod
            def img_to_array(img):
                return _img_to_array(img)
    except ImportError:
        from tensorflow.keras.applications.mobilenet_v2 import (
            MobileNetV2, preprocess_input, decode_predictions,
        )
        from tensorflow.keras.preprocessing import image as keras_image
except Exception as e:
    st.error(f"TensorFlow failed to load: {e}")
    st.stop()
# ─────────────────────────────────────────────────────────────────────────────

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Woofer Care AI - Smart Pet Analysis",
    page_icon="🐶",
    layout="wide",
    initial_sidebar_state="auto"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── General ── */
  .main { background: #FDF6EC; }
  .block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 3rem;
  }

  /* ── Vet Assistant chat bubbles ── */
  .chat-wrapper { display: flex; flex-direction: column; gap: 12px; margin: 16px 0; }

  .chat-bubble-user {
    align-self: flex-end;
    background: linear-gradient(135deg, #7A4F2E, #C0532A);
    color: white;
    padding: 12px 18px;
    border-radius: 20px 20px 4px 20px;
    max-width: 80%;
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(122,79,46,0.25);
  }

  .chat-bubble-assistant {
    align-self: flex-start;
    background: white;
    color: #2C1A0E;
    padding: 14px 18px;
    border-radius: 20px 20px 20px 4px;
    max-width: 85%;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 2px 12px rgba(44,26,14,0.1);
    border-left: 4px solid #E8A44A;
  }

  .chat-meta {
    font-size: 0.75rem;
    opacity: 0.55;
    margin-top: 4px;
  }

  .vet-header {
    background: linear-gradient(135deg, #2C1A0E 0%, #7A4F2E 100%);
    border-radius: 16px;
    padding: 24px 28px;
    color: white;
    margin-bottom: 20px;
  }
  .vet-header h2 { margin: 0 0 6px 0; font-size: 1.5rem; }
  .vet-header p  { margin: 0; opacity: 0.75; font-size: 0.92rem; }

  .context-pill {
    display: inline-block;
    background: rgba(232,164,74,0.15);
    border: 1px solid rgba(232,164,74,0.4);
    color: #7A4F2E;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    margin: 3px 3px 3px 0;
  }

  .disclaimer-box {
    background: #FEF3E2;
    border: 1px solid #E8A44A;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 0.82rem;
    color: #7A4F2E;
    margin-top: 12px;
  }

  /* ── Quick symptom chips ── */
  div[data-testid="stHorizontalBlock"] button {
    border-radius: 20px !important;
    font-size: 0.82rem !important;
  }

  div[data-testid="stTabs"] button {
    white-space: nowrap;
  }

  div[data-testid="stDownloadButton"] button,
  div[data-testid="stFormSubmitButton"] button {
    min-height: 44px;
  }

  pre, code {
    white-space: pre-wrap !important;
    word-break: break-word !important;
  }

  @media (max-width: 768px) {
    .block-container {
      padding: 1rem 0.85rem 2rem;
    }

    h1 { font-size: 1.8rem !important; line-height: 1.15 !important; }
    h2 { font-size: 1.45rem !important; line-height: 1.2 !important; }
    h3 { font-size: 1.18rem !important; line-height: 1.25 !important; }

    .chat-bubble-user,
    .chat-bubble-assistant {
      max-width: 100%;
      padding: 11px 14px;
      font-size: 0.9rem;
    }

    .vet-header {
      border-radius: 12px;
      padding: 18px 16px;
    }

    div[data-testid="stTabs"] div[role="tablist"] {
      gap: 0.25rem;
      overflow-x: auto;
      scrollbar-width: thin;
    }

    div[data-testid="stTabs"] button {
      min-height: 42px;
      padding: 0.35rem 0.7rem;
      font-size: 0.86rem;
    }

    div[data-testid="stHorizontalBlock"] {
      gap: 0.65rem;
    }

    div[data-testid="column"] {
      min-width: 0 !important;
    }

    div[data-testid="stMetric"] {
      background: rgba(255,255,255,0.7);
      border-radius: 12px;
      padding: 0.75rem;
    }

    div[data-testid="stDownloadButton"] button,
    div[data-testid="stButton"] button,
    div[data-testid="stFormSubmitButton"] button,
    .stLinkButton a {
      width: 100%;
      min-height: 44px;
      white-space: normal;
    }
  }
</style>
""", unsafe_allow_html=True)

# ── File paths ────────────────────────────────────────────────────────────────
DB_FILE             = "woofer_care_registry.json"
KNOWLEDGE_BASE_FILE = "dog_care_knowledge.json"
_PROFILE_REPOSITORY = None

# ══════════════════════════════════════════════════════════════════════════════
# GROQ LLM INTEGRATION
# ══════════════════════════════════════════════════════════════════════════════

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

def get_groq_key():
    """Safely retrieve Groq API key from Streamlit secrets."""
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return None


def build_vet_system_prompt(pet: dict) -> str:
    """
    Build a rich, breed-aware system prompt so Llama knows exactly
    who it's talking about before the user says a word.
    """
    breed      = pet.get("breed_detected", "Unknown breed")
    age        = pet.get("age", "unknown age")
    weight     = pet.get("weight", "unknown weight")
    nickname   = pet.get("nickname", "this dog")
    notes      = pet.get("health_notes", "")
    care       = pet.get("care_data", {})
    known_issues = care.get("health", {}).get("common_issues", [])
    diet_type    = care.get("nutrition", {}).get("diet_type", "")
    exercise_req = care.get("exercise", {}).get("daily_requirement", "")
    lifespan     = care.get("health", {}).get("lifespan", "")

    known_str = ", ".join(known_issues) if known_issues else "none on record"

    return f"""You are Woofer Vet Assistant — a knowledgeable, warm, and careful AI veterinary guide built into the Woofer Care AI platform for pet owners in Azerbaijan.

You are currently helping with a specific dog. Here is their full profile:

🐕 Name: {nickname}
🔬 Breed: {breed}
📅 Age: {age} years
⚖️ Weight: {weight} kg
🏥 Known health vulnerabilities for this breed: {known_str}
🥩 Diet type: {diet_type}
🏃 Daily exercise requirement: {exercise_req}
❤️ Expected lifespan: {lifespan}
📝 Owner health notes: {notes if notes else "none provided"}

Your behaviour rules:
1. Always keep the breed, age, and weight in mind when answering — tailor every response to THIS dog specifically.
2. Be warm, clear, and reassuring — owners are often worried when asking health questions.
3. For serious or emergency symptoms (difficulty breathing, collapse, bloat, seizures, uncontrolled bleeding) — always say to go to a vet IMMEDIATELY and make this very clear.
4. For non-emergency symptoms — give helpful guidance, possible causes, and home monitoring tips, but always recommend a vet visit if symptoms persist beyond 24-48 hours.
5. Never diagnose definitively. Say "this may indicate" or "could be related to" rather than "this is definitely".
6. At the end of every response, add a short disclaimer reminding the owner that your advice does not replace a licensed veterinarian.
7. Keep responses concise — 3 to 5 short paragraphs maximum. Use bullet points where helpful.
8. If the user writes in Azerbaijani, respond in Azerbaijani. If in English, respond in English.
9. Reference the breed's known vulnerabilities when relevant — for example if a Golden Retriever shows joint pain, mention hip dysplasia as a possibility.
10. You are part of an ethical, adoption-first platform. If someone asks about buying/selling pets, gently redirect them to adoption."""


def ask_groq(messages: list, system_prompt: str) -> str:
    """Send a conversation to Groq and return the assistant reply."""
    api_key = get_groq_key()
    if not api_key:
        return "⚠️ Groq API key not found. Please add GROQ_API_KEY to your Streamlit secrets."

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": 0.55,
        "max_tokens": 900,
        "stream": False,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "⚠️ Request timed out. Please try again."
    except requests.exceptions.HTTPError as e:
        return f"⚠️ API error: {e.response.status_code} — {e.response.text[:200]}"
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"


# ── Quick symptom suggestions shown as chips ──────────────────────────────────
QUICK_SYMPTOMS = [
    "🤒 Lethargy / low energy",
    "🍽️ Not eating / loss of appetite",
    "🤮 Vomiting",
    "💩 Diarrhea",
    "🐾 Limping / joint pain",
    "😮‍💨 Breathing difficulties",
    "🔴 Skin rash / itching",
    "👁️ Eye discharge / cloudiness",
    "🦻 Ear scratching / smell",
    "⚖️ Rapid weight loss",
    "💧 Excessive thirst / urination",
    "😰 Anxiety / restlessness",
]


def render_vet_chat(pet: dict, chat_key: str):
    """
    Renders the full Vet Assistant chat UI for a given pet.
    chat_key makes session state unique per context (inline vs tab).
    """
    hist_key   = f"vet_history_{chat_key}"
    input_key  = f"vet_input_{chat_key}"
    chip_key   = f"chip_trigger_{chat_key}"

    if hist_key not in st.session_state:
        st.session_state[hist_key] = []

    system_prompt = build_vet_system_prompt(pet)

    # ── Header card ──
    st.markdown(f"""
    <div class="vet-header">
      <h2>🩺 Woofer Vet Assistant</h2>
      <p>AI-powered health guidance for <strong>{pet.get('nickname','your dog')}</strong> — powered by Llama 3 (Groq)</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Context pills showing what the AI knows ──
    st.markdown("**The assistant already knows:**")
    breed   = pet.get("breed_detected", "Unknown")
    age     = pet.get("age", "?")
    weight  = pet.get("weight", "?")
    care    = pet.get("care_data", {})
    issues  = care.get("health", {}).get("common_issues", [])

    pills_html = (
        f'<span class="context-pill">🔬 {breed}</span>'
        f'<span class="context-pill">📅 {age} yrs</span>'
        f'<span class="context-pill">⚖️ {weight} kg</span>'
    )
    for issue in issues[:3]:
        pills_html += f'<span class="context-pill">⚠️ {issue}</span>'
    st.markdown(pills_html, unsafe_allow_html=True)
    st.markdown("")

    # ── Quick symptom chips ──
    st.markdown("**Quick symptoms — click to ask instantly:**")
    cols = st.columns(4)
    for i, symptom in enumerate(QUICK_SYMPTOMS):
        if cols[i % 4].button(symptom, key=f"{chip_key}_{i}", use_container_width=True):
            st.session_state[hist_key].append({"role": "user", "content": symptom})
            with st.spinner("Woofer Vet is thinking..."):
                reply = ask_groq(st.session_state[hist_key], system_prompt)
            st.session_state[hist_key].append({"role": "assistant", "content": reply})
            st.rerun()

    st.divider()

    # ── Chat history ──
    if st.session_state[hist_key]:
        st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
        for msg in st.session_state[hist_key]:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-bubble-user">🧑 {msg["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                # Format assistant response — preserve line breaks
                content = msg["content"].replace("\n", "<br>")
                st.markdown(
                    f'<div class="chat-bubble-assistant">🩺 {content}</div>',
                    unsafe_allow_html=True
                )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👆 Click a symptom chip above or type your question below to start.")

    # ── Text input ──
    st.markdown("")
    with st.form(key=f"chat_form_{chat_key}", clear_on_submit=True):
        col_input, col_send = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                "Describe symptoms or ask a question...",
                placeholder=f"e.g. '{pet.get('nickname','My dog')} has been scratching her ears for 2 days'",
                label_visibility="collapsed",
                key=input_key
            )
        with col_send:
            submitted = st.form_submit_button("Send 🐾", use_container_width=True, type="primary")

        if submitted and user_input.strip():
            st.session_state[hist_key].append({"role": "user", "content": user_input.strip()})
            with st.spinner("Woofer Vet is thinking..."):
                reply = ask_groq(st.session_state[hist_key], system_prompt)
            st.session_state[hist_key].append({"role": "assistant", "content": reply})
            st.rerun()

    # ── Clear chat button ──
    if st.session_state[hist_key]:
        if st.button("🗑️ Clear conversation", key=f"clear_{chat_key}"):
            st.session_state[hist_key] = []
            st.rerun()

    # ── Disclaimer ──
    st.markdown("""
    <div class="disclaimer-box">
      ⚕️ <strong>Medical Disclaimer:</strong> Woofer Vet Assistant provides general guidance only
      and does not replace a licensed veterinarian. For emergencies, contact your vet immediately.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# AZERBAIJAN E-COMMERCE LINKS
# ══════════════════════════════════════════════════════════════════════════════

AZERBAIJAN_PET_STORES = {
    "biopet": {
        "name": "Biopet.az",
        "base_url": "https://biopet.az/index.php?route=product/search&search=",
        "description": "Largest online pet shop in Azerbaijan",
        "icon": "🛒"
    },
    "wolt": {
        "name": "Wolt Azerbaijan",
        "base_url": "https://wolt.com/en/aze/baku/search?q=",
        "description": "Fast delivery pet supplies in Baku",
        "icon": "🚀"
    },
    "tap_az": {
        "name": "Tap.az",
        "base_url": "https://tap.az/elanlar/heyvanlar/heyvanlar-ucun-mehsullar?q%5Bkeywords%5D=",
        "description": "Local classifieds for pet supplies",
        "icon": "📋"
    }
}


def get_azerbaijan_search_links(item_name):
    search_term = urllib.parse.quote(item_name)
    links = {}
    for store_key, store_info in AZERBAIJAN_PET_STORES.items():
        links[store_key] = {
            "name": store_info["name"],
            "url": store_info["base_url"] + search_term,
            "description": store_info["description"],
            "icon": store_info["icon"]
        }
    return links


# ══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE (RAG)
# ══════════════════════════════════════════════════════════════════════════════

def initialize_knowledge_base():
    knowledge_base = {
        "siberian_husky": {
            "breed_names": ["siberian husky", "husky", "eskimo dog", "malamute"],
            "nutrition": {
                "diet_type": "High-protein, grain-free or limited grain",
                "calories_per_day": "1,200-1,600 kcal (adult)",
                "feeding_schedule": "2 meals per day",
                "special_needs": "Prone to zinc deficiency; requires high-quality animal protein",
                "recommended_foods": ["Salmon-based kibble", "Chicken & sweet potato", "Raw diet (vet supervised)"],
                "avoid": ["Grapes", "Onions", "Excessive grains", "Low-quality fillers"]
            },
            "grooming": {
                "brushing": "3-4 times per week (daily during shedding)",
                "bathing": "Every 6-8 weeks or when dirty",
                "nail_trimming": "Every 3-4 weeks",
                "special_notes": "Heavy seasonal shedding (blow coat twice yearly)"
            },
            "exercise": {
                "daily_requirement": "2+ hours of vigorous exercise",
                "activities": ["Running", "Hiking", "Agility training", "Sledding", "Swimming"],
                "mental_stimulation": "Puzzle toys, training sessions, socialization"
            },
            "health": {
                "common_issues": ["Hip dysplasia", "Eye problems (cataracts)", "Hypothyroidism", "Zinc deficiency"],
                "vet_checkups": "Every 6 months",
                "vaccination_schedule": "Core vaccines + rabies as per local law",
                "lifespan": "12-14 years"
            },
            "supplies": [
                {"category": "Food & Nutrition", "items": ["High-protein dry food", "Fish oil supplements", "Zinc supplements"]},
                {"category": "Grooming", "items": ["Undercoat rake", "Slicker brush", "Deshedding tool", "Dog shampoo"]},
                {"category": "Exercise", "items": ["Harness (not collar)", "Long lead (20ft)", "Backpack for hiking", "Cooling mat"]},
                {"category": "Comfort", "items": ["Elevated bed", "Cooling mat", "Durable chew toys", "Puzzle feeder"]}
            ],
            "cost_estimate_monthly": "150-250 AZN",
            "good_for": ["Active families", "Experienced owners", "Cold climates", "Outdoor enthusiasts"],
            "challenges": ["Escape artists", "High prey drive", "Vocal/howling", "Requires extensive exercise"]
        },
        "golden_retriever": {
            "breed_names": ["golden retriever"],
            "nutrition": {
                "diet_type": "Balanced diet with omega fatty acids",
                "calories_per_day": "1,200-1,600 kcal (adult)",
                "feeding_schedule": "2 meals per day",
                "special_needs": "Prone to obesity; monitor portion sizes carefully",
                "recommended_foods": ["Chicken & rice formula", "Fish-based kibble", "Vegetable supplements"],
                "avoid": ["Excessive treats", "Table scraps", "High-fat foods"]
            },
            "grooming": {
                "brushing": "2-3 times per week",
                "bathing": "Every 4-6 weeks",
                "nail_trimming": "Every 3-4 weeks",
                "special_notes": "Moderate shedding year-round, heavy in spring/fall"
            },
            "exercise": {
                "daily_requirement": "1-2 hours daily",
                "activities": ["Fetching", "Swimming", "Walking", "Obedience training"],
                "mental_stimulation": "Retrieval games, scent work, socialization"
            },
            "health": {
                "common_issues": ["Hip/elbow dysplasia", "Heart conditions", "Cancer", "Skin allergies"],
                "vet_checkups": "Every 6 months",
                "vaccination_schedule": "Core vaccines + rabies",
                "lifespan": "10-12 years"
            },
            "supplies": [
                {"category": "Food & Nutrition", "items": ["Weight management formula", "Joint supplements", "Omega-3 fish oil"]},
                {"category": "Grooming", "items": ["Pin brush", "Deshedding tool", "Gentle shampoo", "Ear cleaning solution"]},
                {"category": "Exercise", "items": ["Tennis balls", "Floating toys", "Comfortable harness"]},
                {"category": "Comfort", "items": ["Orthopedic bed", "Cooling vest", "Slow feeder bowl"]}
            ],
            "cost_estimate_monthly": "120-200 AZN",
            "good_for": ["Families with children", "First-time owners", "Therapy work", "Active households"],
            "challenges": ["Shedding", "Mouthiness", "Prone to obesity", "Separation anxiety"]
        },
        "german_shepherd": {
            "breed_names": ["german shepherd", "alsatian"],
            "nutrition": {
                "diet_type": "High-protein, large breed formula",
                "calories_per_day": "1,300-1,800 kcal (adult)",
                "feeding_schedule": "2 meals per day",
                "special_needs": "Joint support crucial; avoid rapid growth in puppies",
                "recommended_foods": ["Large breed adult formula", "Glucosamine-enriched food", "Lean meats"],
                "avoid": ["High-calcium foods (puppies)", "Excessive weight gain"]
            },
            "grooming": {
                "brushing": "3-4 times per week",
                "bathing": "Every 6-8 weeks",
                "nail_trimming": "Every 2-3 weeks",
                "special_notes": "Year-round moderate shedding, heavy twice yearly"
            },
            "exercise": {
                "daily_requirement": "1.5-2 hours daily",
                "activities": ["Obedience training", "Protection work", "Agility", "Tracking"],
                "mental_stimulation": "Advanced training, problem-solving tasks, jobs to do"
            },
            "health": {
                "common_issues": ["Hip/elbow dysplasia", "Degenerative myelopathy", "Bloat", "Allergies"],
                "vet_checkups": "Every 6 months",
                "vaccination_schedule": "Core vaccines + rabies",
                "lifespan": "9-13 years"
            },
            "supplies": [
                {"category": "Food & Nutrition", "items": ["Large breed formula", "Joint supplements", "Digestive enzymes"]},
                {"category": "Grooming", "items": ["Slicker brush", "Undercoat rake", "Nail grinder", "Paw balm"]},
                {"category": "Exercise", "items": ["Training leash", "Agility equipment", "Scent work kits"]},
                {"category": "Comfort", "items": ["Elevated bed", "Chew-resistant toys", "Anxiety wrap"]}
            ],
            "cost_estimate_monthly": "140-220 AZN",
            "good_for": ["Working roles", "Protection", "Active owners", "Training enthusiasts"],
            "challenges": ["Needs firm training", "Potential aggression if not socialized", "Health issues", "Shedding"]
        },
        "french_bulldog": {
            "breed_names": ["french bulldog", "frenchie"],
            "nutrition": {
                "diet_type": "High-quality, easily digestible",
                "calories_per_day": "600-800 kcal (adult)",
                "feeding_schedule": "2 meals per day",
                "special_needs": "Prone to allergies; avoid fillers. Monitor weight (breathing issues)",
                "recommended_foods": ["Limited ingredient diet", "Novel protein sources", "Probiotic supplements"],
                "avoid": ["Common allergens (chicken, beef)", "Overfeeding", "Hard-to-chew kibble"]
            },
            "grooming": {
                "brushing": "Weekly",
                "bathing": "Every 4-6 weeks or as needed",
                "nail_trimming": "Every 2-3 weeks",
                "special_notes": "Facial folds need daily cleaning; sensitive skin"
            },
            "exercise": {
                "daily_requirement": "30-60 minutes (low intensity)",
                "activities": ["Short walks", "Indoor play", "Mental games"],
                "mental_stimulation": "Puzzle toys, short training sessions"
            },
            "health": {
                "common_issues": ["Brachycephalic syndrome", "Skin allergies", "Intervertebral disc disease", "Heat sensitivity"],
                "vet_checkups": "Every 4-6 months",
                "vaccination_schedule": "Core vaccines + rabies",
                "lifespan": "10-12 years"
            },
            "supplies": [
                {"category": "Food & Nutrition", "items": ["Hypoallergenic formula", "Probiotics", "Elevated feeding bowl"]},
                {"category": "Grooming", "items": ["Wrinkle wipes", "Gentle shampoo", "Nail clippers", "Cooling coat"]},
                {"category": "Exercise", "items": ["Harness (never collar)", "Cooling vest", "Indoor toys"]},
                {"category": "Comfort", "items": ["Cooling mat", "Elevated bed", "Breathable bedding"]}
            ],
            "cost_estimate_monthly": "100-180 AZN",
            "good_for": ["Apartment living", "Low-activity owners", "Companion pet", "Small spaces"],
            "challenges": ["Health issues", "Cannot swim", "Heat intolerance", "Expensive veterinary care"]
        },
        "labrador_retriever": {
            "breed_names": ["labrador retriever", "labrador"],
            "nutrition": {
                "diet_type": "Weight management formula (prone to obesity)",
                "calories_per_day": "1,200-1,600 kcal (adult)",
                "feeding_schedule": "2 meals per day",
                "special_needs": "Measure food carefully; will overeat",
                "recommended_foods": ["Weight control formula", "High-fiber foods", "Lean proteins"],
                "avoid": ["Free feeding", "High-calorie treats", "Table scraps"]
            },
            "grooming": {
                "brushing": "2-3 times per week",
                "bathing": "Every 6-8 weeks",
                "nail_trimming": "Every 3-4 weeks",
                "special_notes": "Water-resistant coat, moderate shedding"
            },
            "exercise": {
                "daily_requirement": "1-2 hours daily",
                "activities": ["Swimming", "Fetching", "Dock diving", "Walking"],
                "mental_stimulation": "Retrieval games, food puzzles, obedience"
            },
            "health": {
                "common_issues": ["Obesity", "Hip/elbow dysplasia", "Ear infections", "Exercise-induced collapse"],
                "vet_checkups": "Every 6 months",
                "vaccination_schedule": "Core vaccines + rabies",
                "lifespan": "10-12 years"
            },
            "supplies": [
                {"category": "Food & Nutrition", "items": ["Weight management kibble", "Measuring cups", "Low-calorie treats"]},
                {"category": "Grooming", "items": ["Rubber curry brush", "Ear cleaner", "Towels"]},
                {"category": "Exercise", "items": ["Floating toys", "Chuck-it launcher", "Life jacket"]},
                {"category": "Comfort", "items": ["Durable bed", "Chew toys", "Slow feeder bowl"]}
            ],
            "cost_estimate_monthly": "120-200 AZN",
            "good_for": ["Families", "Active owners", "Water activities", "First-time owners"],
            "challenges": ["Food obsession", "Shedding", "Chewing (puppies)", "Joint issues"]
        },
        "general_dog": {
            "breed_names": ["mixed breed", "unknown", "mixed"],
            "nutrition": {
                "diet_type": "Balanced commercial or vet-recommended diet",
                "calories_per_day": "Varies by size (consult vet)",
                "feeding_schedule": "2 meals per day",
                "special_needs": "Monitor for allergies and sensitivities",
                "recommended_foods": ["High-quality commercial food", "Vet-prescribed diets if needed"],
                "avoid": ["Toxic foods", "Table scraps", "Sudden diet changes"]
            },
            "grooming": {
                "brushing": "Varies by coat type",
                "bathing": "Every 4-8 weeks",
                "nail_trimming": "Every 3-4 weeks",
                "special_notes": "Adapt grooming to coat type and activity level"
            },
            "exercise": {
                "daily_requirement": "30 minutes - 2 hours depending on size/age",
                "activities": ["Walking", "Playtime", "Training"],
                "mental_stimulation": "Interactive toys, training, socialization"
            },
            "health": {
                "common_issues": ["Dental disease", "Obesity", "Parasites"],
                "vet_checkups": "Annual (bi-annual for seniors)",
                "vaccination_schedule": "Core vaccines as recommended by vet",
                "lifespan": "Varies significantly"
            },
            "supplies": [
                {"category": "Essentials", "items": ["Quality dog food", "Food/water bowls", "Collar and leash", "ID tags"]},
                {"category": "Health", "items": ["Flea/tick prevention", "Heartworm prevention", "First aid kit"]},
                {"category": "Comfort", "items": ["Bed", "Toys", "Crate (optional)"]}
            ],
            "cost_estimate_monthly": "80-150 AZN",
            "good_for": ["Varies by individual temperament"],
            "challenges": ["Unknown genetic health risks", "Variable exercise needs"]
        }
    }
    with open(KNOWLEDGE_BASE_FILE, "w") as f:
        json.dump(knowledge_base, f, indent=4)
    return knowledge_base


def load_knowledge_base():
    if os.path.exists(KNOWLEDGE_BASE_FILE):
        with open(KNOWLEDGE_BASE_FILE, "r") as f:
            return json.load(f)
    return initialize_knowledge_base()


def get_breed_info(knowledge_base, breed_label):
    breed_label = breed_label.lower().replace('_', ' ')
    for breed_key, data in knowledge_base.items():
        if any(name in breed_label for name in data["breed_names"]):
            return breed_key, data
    for breed_key, data in knowledge_base.items():
        for name in data["breed_names"]:
            if name in breed_label or breed_label in name:
                return breed_key, data
    return "general_dog", knowledge_base["general_dog"]


# ══════════════════════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════════════════════

def get_profile_repository():
    global _PROFILE_REPOSITORY
    if _PROFILE_REPOSITORY is None:
        try:
            _PROFILE_REPOSITORY = create_pet_profile_repository(DB_FILE, st.secrets)
        except StorageConfigurationError as exc:
            st.error(f"Storage is not configured correctly: {exc}")
            st.stop()
    return _PROFILE_REPOSITORY


def save_to_db(data):
    return get_profile_repository().save(data)


def load_all_pets():
    return get_profile_repository().load_all()


def update_pet_profile(profile_id, updates):
    return get_profile_repository().update(profile_id, updates)


# ══════════════════════════════════════════════════════════════════════════════
# PDF GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def create_care_guide_pdf(pet_data, breed_info, breed_display_name):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(200, 15, "WOOFER CARE AI - PERSONALIZED GUIDE", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, f"Pet Profile: {pet_data.get('nickname', 'Unknown')}", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(200, 8, f"Breed: {breed_display_name}", ln=True)
    pdf.cell(200, 8, f"Profile ID: {pet_data.get('profile_id', 'N/A')}", ln=True)
    pdf.cell(200, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(5)

    nutrition = breed_info.get('nutrition', {})
    pdf.set_font("Arial", "B", 13)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(200, 10, " NUTRITION & DIET", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, 8, f"Diet Type: {nutrition.get('diet_type', 'N/A')}", ln=True)
    pdf.cell(200, 8, f"Daily Calories: {nutrition.get('calories_per_day', 'N/A')}", ln=True)
    pdf.cell(200, 8, f"Feeding Schedule: {nutrition.get('feeding_schedule', 'N/A')}", ln=True)
    pdf.cell(200, 8, "Recommended Foods:", ln=True)
    pdf.set_font("Arial", size=10)
    for food in nutrition.get('recommended_foods', []):
        pdf.cell(200, 6, f"  - {food}", ln=True)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, 8, "Foods to Avoid:", ln=True)
    pdf.set_font("Arial", size=10)
    for food in nutrition.get('avoid', []):
        pdf.cell(200, 6, f"  - {food}", ln=True)
    pdf.ln(5)

    exercise = breed_info.get('exercise', {})
    pdf.set_font("Arial", "B", 13)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(200, 10, " EXERCISE REQUIREMENTS", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, 8, f"Daily Requirement: {exercise.get('daily_requirement', 'N/A')}", ln=True)
    pdf.cell(200, 8, "Recommended Activities:", ln=True)
    pdf.set_font("Arial", size=10)
    for activity in exercise.get('activities', []):
        pdf.cell(200, 6, f"  - {activity}", ln=True)
    pdf.ln(5)

    health = breed_info.get('health', {})
    pdf.set_font("Arial", "B", 13)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(200, 10, " HEALTH & WELLNESS", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, 8, f"Lifespan: {health.get('lifespan', 'N/A')}", ln=True)
    pdf.cell(200, 8, f"Vet Checkups: {health.get('vet_checkups', 'N/A')}", ln=True)
    pdf.cell(200, 8, "Common Health Issues to Monitor:", ln=True)
    pdf.set_font("Arial", size=10)
    for issue in health.get('common_issues', []):
        pdf.cell(200, 6, f"  - {issue}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 13)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(200, 10, " RECOMMENDED SUPPLIES", ln=True, fill=True)
    pdf.ln(2)
    for category in breed_info.get('supplies', []):
        pdf.set_font("Arial", "B", 11)
        pdf.cell(200, 8, f"{category['category']}:", ln=True)
        pdf.set_font("Arial", size=10)
        for item in category['items']:
            pdf.cell(200, 6, f"  - {item}", ln=True)
        pdf.ln(2)

    pdf.ln(10)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, "Disclaimer: This guide is generated by AI analysis and should be used as general guidance. "
                         "Always consult with a licensed veterinarian for specific medical advice.")
    return bytes(pdf.output())


# ══════════════════════════════════════════════════════════════════════════════
# AI BREED MODEL
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def load_woofer_model():
    return MobileNetV2(weights='imagenet')


def predict_breed(img):
    model = load_woofer_model()
    img = img.convert("RGB")
    img   = img.resize((224, 224))
    x     = keras_image.img_to_array(img)
    x     = np.expand_dims(x, axis=0)
    x     = preprocess_input(x)
    preds = model.predict(x, verbose=0)
    results = decode_predictions(preds, top=5)[0]

    dog_breeds = {
        'siberian_husky':    ['siberian_husky', 'eskimo_dog', 'malamute'],
        'golden_retriever':  ['golden_retriever'],
        'labrador_retriever':['labrador_retriever'],
        'german_shepherd':   ['german_shepherd', 'malinois'],
        'french_bulldog':    ['french_bulldog', 'bulldog'],
        'beagle':            ['beagle'],
        'poodle':            ['standard_poodle', 'miniature_poodle', 'toy_poodle'],
        'rottweiler':        ['rottweiler'],
        'yorkshire_terrier': ['yorkshire_terrier'],
        'boxer':             ['boxer'],
        'dachshund':         ['dachshund'],
        'pomeranian':        ['pomeranian'],
        'chihuahua':         ['chihuahua'],
        'border_collie':     ['border_collie', 'collie'],
        'shih_tzu':          ['shih_tzu'],
        'pug':               ['pug'],
        'cocker_spaniel':    ['cocker_spaniel', 'english_setter'],
        'doberman':          ['doberman'],
        'great_dane':        ['great_dane'],
        'schnauzer':         ['schnauzer', 'miniature_schnauzer']
    }

    for imagenet_id, label, confidence in results:
        label_lower = label.lower()
        for breed_key, aliases in dog_breeds.items():
            if any(alias in label_lower for alias in aliases):
                return breed_key.replace('_', ' ').title(), confidence
        if 'dog' in label_lower or 'hound' in label_lower or 'terrier' in label_lower:
            return label.replace('_', ' ').title(), confidence

    return results[0][1].replace('_', ' ').title(), results[0][2]


# ══════════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════

def render_header():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://img.icons8.com/color/96/dog.png", width=80)
    with col2:
        st.title("Woofer Care AI")
        st.markdown("**Intelligent Pet Analysis & Personalized Care Recommendations**")
        st.caption("🐕 Promoting Responsible Pet Ownership Through AI")
    st.markdown("---")


def render_sidebar():
    with st.sidebar:
        st.header("About Woofer Care AI")
        st.info("""
        **Mission:** Empower pet owners with AI-driven insights for better care.

        **How it works:**
        1. Upload your dog's photo
        2. AI analyzes breed characteristics
        3. Get personalized care recommendations
        4. Chat with the Vet Assistant about symptoms
        5. Track health and supplies

        **Ethical Commitment:**
        - We do not support pet sales or breeding
        - Focus on adoption support and welfare
        - Educational resources for responsible ownership
        """)
        st.divider()
        pets = load_all_pets()
        st.metric("Pets Analyzed", len(pets))
        st.caption(f"Storage: {get_profile_repository().public_label}")
        if pets:
            st.caption(f"Last analysis: {pets[-1].get('created_at', 'N/A')[:10]}")

        # API status indicator
        st.divider()
        key = get_groq_key()
        if key:
            st.success("🟢 Vet Assistant: Online")
        else:
            st.error("🔴 Vet Assistant: API key missing")


def render_breed_analysis():
    st.header("🔬 Step 1: AI Breed Analysis")
    st.markdown("Upload your dog's photo to receive instant breed identification and personalized care recommendations.")

    col1, col2 = st.columns([1, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "📸 Upload Dog Photo", type=["jpg", "jpeg", "png"],
            help="Clear, well-lit photos work best"
        )

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)

            with st.form("pet_profile_form"):
                st.subheader("Pet Information")
                nickname = st.text_input("Pet Nickname *", placeholder="e.g., Max, Bella")

                col_age, col_weight = st.columns(2)
                with col_age:
                    age = st.number_input("Age (years)", min_value=0.0, max_value=30.0, value=2.0, step=0.5)
                with col_weight:
                    weight = st.number_input("Weight (kg)", min_value=0.1, max_value=100.0, value=10.0, step=0.5)

                health_notes = st.text_area(
                    "Health Notes (Optional)",
                    placeholder="Any known allergies, conditions, or special needs..."
                )

                submit_button = st.form_submit_button(
                    "🔍 Analyze & Create Care Profile",
                    use_container_width=True, type="primary"
                )

                if submit_button and nickname:
                    with st.spinner("Analyzing breed characteristics..."):
                        breed, confidence = predict_breed(image)
                        knowledge_base = load_knowledge_base()
                        breed_key, breed_data = get_breed_info(knowledge_base, breed)

                        pet_data = {
                            "nickname":       nickname,
                            "breed_detected": breed,
                            "ai_confidence":  f"{confidence:.1%}",
                            "age":            age,
                            "weight":         weight,
                            "health_notes":   health_notes,
                            "breed_key":      breed_key,
                            "care_data":      breed_data
                        }
                        saved_pet = save_to_db(pet_data)
                        profile_id = saved_pet["profile_id"]
                        st.session_state['current_pet']       = saved_pet
                        st.session_state['analysis_complete'] = True
                        st.success(f"✅ Profile created! ID: {profile_id}")
                        st.rerun()

    with col2:
        if st.session_state.get('analysis_complete') and st.session_state.get('current_pet'):
            pet        = st.session_state['current_pet']
            breed_data = pet['care_data']

            st.subheader("📊 Analysis Results")
            conf_float = float(pet['ai_confidence'].strip('%')) / 100
            st.progress(conf_float, text=f"AI Confidence: {pet['ai_confidence']}")
            st.metric("Detected Breed", pet['breed_detected'])
            st.metric("Estimated Monthly Care Cost", breed_data.get('cost_estimate_monthly', 'N/A'))

            st.subheader("Quick Care Stats")
            cols = st.columns(3)
            with cols[0]:
                st.metric("Daily Exercise",
                          breed_data.get('exercise', {}).get('daily_requirement', 'N/A').split()[0] + "h")
            with cols[1]:
                st.metric("Grooming",
                          breed_data.get('grooming', {}).get('brushing', 'N/A').split()[0] + "x/week")
            with cols[2]:
                st.metric("Lifespan",
                          breed_data.get('health', {}).get('lifespan', 'N/A').split()[0] + " yrs")

            pdf_bytes = create_care_guide_pdf(pet, breed_data, pet['breed_detected'])
            st.download_button(
                label="📥 Download Full Care Guide (PDF)",
                data=pdf_bytes,
                file_name=f"Woofer_Care_Guide_{pet['nickname']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.info("👈 Upload a photo and fill out the form to see AI analysis results here.")

    # ── INLINE VET ASSISTANT (appears after analysis) ──────────────────────
    if st.session_state.get('analysis_complete') and st.session_state.get('current_pet'):
        st.markdown("---")
        pet = st.session_state['current_pet']
        st.markdown(f"### 🩺 Ask the Vet Assistant about {pet.get('nickname', 'your dog')}")
        st.caption("Describe symptoms or health concerns — the assistant already knows the breed, age, and weight.")
        render_vet_chat(pet, chat_key="inline")


def render_care_recommendations():
    st.header("📋 Step 2: Personalized Care Plan")

    pets = load_all_pets()
    if not pets:
        st.warning("No pet profiles found. Please analyze a pet in Step 1 first.")
        return

    selected_pet_name = st.selectbox(
        "Select Pet Profile",
        options=[f"{p['nickname']} ({p['breed_detected']}) - {p['profile_id']}" for p in reversed(pets)],
        index=0
    )
    selected_profile_id = selected_pet_name.split(" - ")[-1]
    selected_pet = next((p for p in pets if p['profile_id'] == selected_profile_id), None)

    if not selected_pet:
        st.error("Could not load pet data.")
        return

    breed_data = selected_pet.get('care_data', {})
    care_tabs  = st.tabs(["🍖 Nutrition", "🏃 Exercise", "✨ Grooming", "🏥 Health", "🛒 Supplies"])

    with care_tabs[0]:
        st.subheader("Dietary Recommendations")
        nutrition = breed_data.get('nutrition', {})
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Diet Type:** {nutrition.get('diet_type', 'N/A')}")
            st.markdown(f"**Daily Calories:** {nutrition.get('calories_per_day', 'N/A')}")
            st.markdown(f"**Feeding Schedule:** {nutrition.get('feeding_schedule', 'N/A')}")
            st.markdown(f"**Special Needs:** {nutrition.get('special_needs', 'N/A')}")
        with col2:
            st.markdown("**✅ Recommended Foods:**")
            for food in nutrition.get('recommended_foods', []):
                st.markdown(f"- {food}")
            st.markdown("**❌ Foods to Avoid:**")
            for food in nutrition.get('avoid', []):
                st.markdown(f"- {food}")
        st.divider()
        st.subheader("🛒 Shop in Azerbaijan")
        if nutrition.get('recommended_foods'):
            links = get_azerbaijan_search_links(nutrition['recommended_foods'][0])
            cols  = st.columns(3)
            for idx, (store_key, store_info) in enumerate(links.items()):
                with cols[idx]:
                    st.markdown(f"**{store_info['icon']} {store_info['name']}**")
                    st.caption(store_info['description'])
                    st.link_button(f"Search {store_info['name']}", store_info['url'], use_container_width=True)

    with care_tabs[1]:
        st.subheader("Exercise Plan")
        exercise = breed_data.get('exercise', {})
        st.markdown(f"**Daily Requirement:** {exercise.get('daily_requirement', 'N/A')}")
        st.markdown("**🏆 Recommended Activities:**")
        for activity in exercise.get('activities', []):
            st.markdown(f"- {activity}")
        st.markdown(f"**🧠 Mental Stimulation:** {exercise.get('mental_stimulation', 'N/A')}")
        st.divider()
        st.subheader("📅 Daily Exercise Tracker")
        today_exercise = st.number_input("Minutes exercised today", min_value=0, max_value=300, value=30)
        target = 120
        try:
            target = int(exercise.get('daily_requirement', '2').split()[0]) * 60
        except:
            pass
        progress = min(today_exercise / target, 1.0)
        st.progress(progress, text=f"{today_exercise}/{target} minutes ({progress:.0%})")
        if progress >= 1.0:
            st.success("🎉 Daily exercise goal achieved!")
        else:
            st.info(f"💪 {target - today_exercise} more minutes to reach today's goal")

    with care_tabs[2]:
        st.subheader("Grooming Schedule")
        grooming = breed_data.get('grooming', {})
        cols = st.columns(3)
        with cols[0]: st.metric("Brushing", grooming.get('brushing', 'N/A'))
        with cols[1]: st.metric("Bathing",  grooming.get('bathing', 'N/A'))
        with cols[2]: st.metric("Nails",    grooming.get('nail_trimming', 'N/A'))
        st.info(f"**Special Notes:** {grooming.get('special_notes', 'N/A')}")
        st.divider()
        st.subheader("✅ This Week's Grooming Checklist")
        c1, c2, c3 = st.columns(3)
        with c1: st.checkbox("Brushing Session")
        with c2: st.checkbox("Nail Check")
        with c3: st.checkbox("Ear Cleaning")

    with care_tabs[3]:
        st.subheader("Health Monitoring")
        health = breed_data.get('health', {})
        st.markdown(f"**Expected Lifespan:** {health.get('lifespan', 'N/A')}")
        st.markdown(f"**Recommended Vet Visits:** {health.get('vet_checkups', 'N/A')}")
        st.markdown("**⚠️ Common Health Issues to Monitor:**")
        for issue in health.get('common_issues', []):
            st.markdown(f"- {issue}")
        st.divider()
        st.subheader("🏥 Health Records")
        vet_date  = st.date_input("Last Vet Visit", value=datetime.now() - timedelta(days=30))
        next_due  = st.date_input("Next Appointment Due", value=datetime.now() + timedelta(days=60))
        days_until = (next_due - datetime.now().date()).days
        if days_until < 7:
            st.error(f"⚠️ Vet appointment due in {days_until} days!")
        elif days_until < 30:
            st.warning(f"⏰ Vet appointment coming up in {days_until} days")
        else:
            st.success(f"✅ Next checkup in {days_until} days")
        if selected_pet.get('health_notes'):
            st.info(f"**Your Notes:** {selected_pet['health_notes']}")

    with care_tabs[4]:
        st.subheader("Recommended Supplies")
        for category in breed_data.get('supplies', []):
            with st.expander(f"📦 {category['category']}"):
                for item in category['items']:
                    cols = st.columns([3, 1])
                    with cols[0]:
                        st.markdown(f"- **{item}**")
                    with cols[1]:
                        links = get_azerbaijan_search_links(item)
                        store_options = {f"{v['icon']} {v['name']}": v['url'] for k, v in links.items()}
                        selected_store = st.selectbox(
                            "Choose store", options=list(store_options.keys()),
                            key=f"store_{category['category']}_{item}",
                            label_visibility="collapsed"
                        )
                        if selected_store:
                            st.link_button("🛒 Buy Now", store_options[selected_store], use_container_width=True)
        st.divider()
        st.caption("Affiliate links support our mission. We never earn from animal sales.")


def render_vet_assistant_tab():
    """Dedicated full-page Vet Assistant tab."""
    st.header("🩺 Vet Assistant")
    st.markdown("Select a pet profile and chat with our AI vet powered by **Llama 3 via Groq**.")

    pets = load_all_pets()
    if not pets:
        st.warning("No pets analyzed yet. Go to **AI Analysis** first to create a profile.")
        return

    selected_pet_name = st.selectbox(
        "Which pet do you want to ask about?",
        options=[f"{p['nickname']} ({p['breed_detected']}) — {p['profile_id']}" for p in reversed(pets)],
        index=0
    )
    selected_profile_id = selected_pet_name.split("— ")[-1].strip()
    selected_pet = next((p for p in pets if p['profile_id'] == selected_profile_id), None)

    if not selected_pet:
        st.error("Could not load pet data.")
        return

    st.markdown("---")
    render_vet_chat(selected_pet, chat_key=f"tab_{selected_profile_id}")


def render_health_tracker():
    st.header("🏥 Health & Wellness Tracker")
    pets = load_all_pets()
    if not pets:
        st.warning("No pets registered yet. Please create a profile in Step 1.")
        return

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total Pets Tracked", len(pets))
    with col2:
        avg_age = sum(p.get('age', 0) for p in pets) / len(pets)
        st.metric("Average Age", f"{avg_age:.1f} years")
    with col3: st.metric("Care Guides Generated", len(pets))

    st.subheader("Your Pets' Health Overview")
    for pet in reversed(pets[-5:]):
        with st.expander(f"🐕 {pet['nickname']} ({pet['breed_detected']})"):
            cols = st.columns([2, 2, 1])
            with cols[0]:
                st.markdown(f"**Age:** {pet.get('age', 'N/A')} years")
                st.markdown(f"**Weight:** {pet.get('weight', 'N/A')} kg")
            with cols[1]:
                created_date = datetime.fromisoformat(pet.get('created_at', datetime.now().isoformat()))
                days_since   = (datetime.now() - created_date).days
                st.markdown(f"**Profile Age:** {days_since} days")
                st.markdown(f"**AI Confidence:** {pet.get('ai_confidence', 'N/A')}")

    st.divider()
    st.subheader("⏰ Care Reminders")
    reminder_type = st.selectbox("Set New Reminder",
                                 ["Vet Appointment", "Vaccination", "Grooming", "Medication", "Buy Food"])
    reminder_date = st.date_input("Reminder Date", min_value=datetime.now().date())
    reminder_note = st.text_input("Notes")
    if st.button("Add Reminder"):
        st.success(f"✅ Reminder set: {reminder_type} on {reminder_date}")


def render_trust_passport():
    st.header("Trust Passport & Compliance Readiness")
    st.markdown(
        "Create a country-aware readiness document for adoption, fostering, vet referral, "
        "or responsible owner transfer. This is intentionally not an escrow or live-animal sales flow."
    )
    st.info(
        "Strategic lane: keep Woofer adoption-first now. Treat marketplace listings, breeder payments, "
        "and escrow as future restricted features that require legal and payment-provider review."
    )

    pets = load_all_pets()
    if not pets:
        st.warning("No pet profiles found. Create a profile in AI Analysis first.")
        return

    selected_pet_name = st.selectbox(
        "Select Pet Profile",
        options=[f"{p['nickname']} ({p['breed_detected']}) - {p['profile_id']}" for p in reversed(pets)],
        index=0,
        key="trust_passport_pet",
    )
    selected_profile_id = selected_pet_name.split(" - ")[-1]
    selected_pet = next((p for p in pets if p["profile_id"] == selected_profile_id), None)
    if not selected_pet:
        st.error("Could not load pet data.")
        return

    market = st.selectbox(
        "Target market",
        options=list(COMPLIANCE_MARKETS.keys()),
        index=0,
        key="trust_passport_market",
    )
    market_profile = COMPLIANCE_MARKETS[market]

    col_summary, col_market = st.columns([1, 1])
    with col_summary:
        st.subheader("Profile Snapshot")
        st.metric("Breed estimate", selected_pet.get("breed_detected", "Unknown"))
        st.metric("AI confidence", selected_pet.get("ai_confidence", "N/A"))
        st.caption(f"Profile ID: {selected_pet.get('profile_id', 'N/A')}")

    with col_market:
        st.subheader("Market Position")
        st.markdown(market_profile["position"])
        st.warning(market_profile["blocked_until"])

    st.subheader("Readiness Checklist")
    checks = {}
    for item in TRUST_PASSPORT_CHECKS:
        checks[item["id"]] = st.checkbox(
            item["label"],
            help=item["help"],
            key=f"trust_{selected_profile_id}_{item['id']}",
        )

    score = calculate_readiness_score(checks)
    missing_checks = get_missing_readiness_checks(checks)
    st.progress(score / 100, text=f"Readiness score: {score}%")
    if score >= 80:
        st.success("Strong enough for partner review. Still verify legal requirements before any transfer.")
    elif score >= 50:
        st.warning("Partially ready. Collect the missing records before presenting this to a partner.")
    else:
        st.error("Not ready for transfer/adoption review yet.")

    with st.expander("Country notes", expanded=True):
        for note in market_profile["notes"]:
            st.markdown(f"- {note}")

    with st.expander("Missing evidence and next steps", expanded=bool(missing_checks)):
        if missing_checks:
            st.markdown("Collect these items before presenting the passport to a partner:")
            for item in missing_checks:
                st.markdown(f"- **{item['label']}** - {item['help']}")
        else:
            st.success("All readiness evidence items are marked complete.")

    operator_notes = st.text_area(
        "Operator notes",
        placeholder="Example: shelter contact, vet clinic name, vaccination proof location, follow-up date...",
        key=f"trust_notes_{selected_profile_id}",
    )
    passport_md = build_trust_passport(selected_pet, market, checks, operator_notes)
    passport_pdf = build_trust_passport_pdf(selected_pet, market, checks, operator_notes)
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", selected_pet.get("nickname", "woofer")).strip("_")

    col_markdown, col_pdf = st.columns(2)
    with col_markdown:
        st.download_button(
            "Download Markdown",
            data=passport_md.encode("utf-8"),
            file_name=f"Woofer_Trust_Passport_{safe_name or 'pet'}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_pdf:
        st.download_button(
            "Download PDF",
            data=passport_pdf,
            file_name=f"Woofer_Trust_Passport_{safe_name or 'pet'}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.subheader("Generated Preview")
    st.code(passport_md, language="markdown")


def render_adoption_support():
    st.header("🏠 Adoption & Welfare Support")
    st.markdown("""
    ### Our Ethical Stance
    At Woofer Care AI, we believe every pet deserves a loving home. We do not support commercial breeding
    or pet sales. Instead, we focus on supporting adopters with AI-powered care guidance.
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🐾 Why Adopt?")
        st.markdown("""
        - **Save a Life:** Millions of healthy pets need homes
        - **Combat Puppy Mills:** Adoption doesn't support cruel operations
        - **Adult Pets Available:** Skip the destructive puppy phase
        - **Cost Effective:** Adoption fees include vaccinations
        """)
        st.subheader("📚 Pre-Adoption Checklist")
        for item in [
            "Research breed-specific needs (use our AI tool!)",
            "Calculate monthly costs (food, vet, supplies)",
            "Ensure your housing allows pets",
            "Plan for exercise and socialization time",
            "Find a local veterinarian",
            "Pet-proof your home"
        ]:
            st.checkbox(item, key=f"adopt_{item}")
    with col2:
        st.subheader("🏥 Local Resources (Azerbaijan)")
        st.info("""
        **Veterinary Clinics:**
        - VetCity Baku
        - Animal Care Center
        - Pet Veterinary Clinic

        **Shelters & Rescues:**
        - Baku Animal Rescue
        - Stray Animals Center
        - Volunteer-based rescue groups
        """)
        st.subheader("💝 How to Help")
        st.markdown("""
        - **Foster:** Temporarily house pets waiting for homes
        - **Volunteer:** Help at local shelters
        - **Donate:** Support welfare organizations
        - **Educate:** Share responsible ownership knowledge
        """)
    st.divider()
    st.caption("Contact us to get involved!")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    if not os.path.exists(KNOWLEDGE_BASE_FILE):
        initialize_knowledge_base()

    render_header()
    render_sidebar()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔬 AI Analysis",
        "📋 Care Plan",
        "🩺 Vet Assistant",
        "🏥 Health Tracker",
        "Trust Passport",
        "🏠 Adoption Support"
    ])

    with tab1: render_breed_analysis()
    with tab2: render_care_recommendations()
    with tab3: render_vet_assistant_tab()
    with tab4: render_health_tracker()
    with tab5: render_trust_passport()
    with tab6: render_adoption_support()

    st.markdown("---")
    st.caption("""
    **Woofer Care AI** | Promoting Responsible Pet Ownership through Technology |
    © 2025 Woofer Project | Vet Assistant powered by Llama 3 via Groq
    """)


if __name__ == "__main__":
    main()
