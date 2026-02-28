import streamlit as st
import numpy as np
from PIL import Image
import time
import uuid
import json
import os
from datetime import datetime, timedelta
from fpdf import FPDF
import re
import urllib.parse

# ── Tensorflow / Keras ────────────────────────────────────────────────────────
# tensorflow-cpu >= 2.20 supports Python 3.13 (Streamlit Cloud default).
# In tf 2.16+, Keras became a standalone package — imports changed.
try:
    import tensorflow as tf
    try:
        # tf 2.16+ / 2.20+ style (keras is a separate package)
        from keras.applications.mobilenet_v2 import (
            MobileNetV2,
            preprocess_input,
            decode_predictions,
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
        # tf 2.15 and older style
        from tensorflow.keras.applications.mobilenet_v2 import (
            MobileNetV2,
            preprocess_input,
            decode_predictions,
        )
        from tensorflow.keras.preprocessing import image as keras_image

except Exception as e:
    st.error(f"TensorFlow failed to load: {e}")
    st.stop()
# ─────────────────────────────────────────────────────────────────────────────

# Page Configuration
st.set_page_config(
    page_title="Woofer Care AI - Smart Pet Analysis",
    page_icon="🐶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# File paths
DB_FILE = "woofer_care_registry.json"
KNOWLEDGE_BASE_FILE = "dog_care_knowledge.json"

# ==================== AZERBAIJAN E-COMMERCE LINKS ====================

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
    """
    Generate search links for Azerbaijani pet stores
    Returns dict of store names and their search URLs
    """
    # Clean and encode the search term
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


# ==================== KNOWLEDGE BASE (RAG System) ====================

def initialize_knowledge_base():
    """Initialize comprehensive dog care knowledge base"""
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
                {"category": "Food & Nutrition",
                 "items": ["High-protein dry food", "Fish oil supplements", "Zinc supplements"]},
                {"category": "Grooming",
                 "items": ["Undercoat rake", "Slicker brush", "Deshedding tool", "Dog shampoo"]},
                {"category": "Exercise",
                 "items": ["Harness (not collar)", "Long lead (20ft)", "Backpack for hiking", "Cooling mat"]},
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
                {"category": "Food & Nutrition",
                 "items": ["Weight management formula", "Joint supplements", "Omega-3 fish oil"]},
                {"category": "Grooming",
                 "items": ["Pin brush", "Deshedding tool", "Gentle shampoo", "Ear cleaning solution"]},
                {"category": "Exercise", "items": ["Tennis balls", "Floating toys", "Comfortable harness"]},
                {"category": "Comfort", "items": ["Orthopedic bed", "Cooling vest", "Slow feeder bowl"]}
            ],
            "cost_estimate_monthly": "120-200 AZN",
            "good_for": ["Families with children", "First-time owners", "Therapy work", "Active households"],
            "challenges": ["Shedding", "Mouthiness (carrying things)", "Prone to obesity", "Separation anxiety"]
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
                {"category": "Food & Nutrition",
                 "items": ["Large breed formula", "Joint supplements", "Digestive enzymes"]},
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
                "common_issues": ["Brachycephalic syndrome", "Skin allergies", "Intervertebral disc disease",
                                  "Heat sensitivity"],
                "vet_checkups": "Every 4-6 months",
                "vaccination_schedule": "Core vaccines + rabies",
                "lifespan": "10-12 years"
            },
            "supplies": [
                {"category": "Food & Nutrition",
                 "items": ["Hypoallergenic formula", "Probiotics", "Elevated feeding bowl"]},
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
                {"category": "Food & Nutrition",
                 "items": ["Weight management kibble", "Measuring cups", "Low-calorie treats"]},
                {"category": "Grooming", "items": ["Rubber curry brush", "Ear cleaner", "Towels (love water)"]},
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
                {"category": "Essentials",
                 "items": ["Quality dog food", "Food/water bowls", "Collar and leash", "ID tags"]},
                {"category": "Health", "items": ["Flea/tick prevention", "Heartworm prevention", "First aid kit"]},
                {"category": "Comfort", "items": ["Bed", "Toys", "Crate (optional)"]}
            ],
            "cost_estimate_monthly": "80-150 AZN",
            "good_for": ["Varies by individual temperament"],
            "challenges": ["Unknown genetic health risks", "Variable exercise needs"]
        }
    }

    # Save to file for persistence
    with open(KNOWLEDGE_BASE_FILE, "w") as f:
        json.dump(knowledge_base, f, indent=4)

    return knowledge_base


def load_knowledge_base():
    """Load or initialize the knowledge base"""
    if os.path.exists(KNOWLEDGE_BASE_FILE):
        with open(KNOWLEDGE_BASE_FILE, "r") as f:
            return json.load(f)
    else:
        return initialize_knowledge_base()


def get_breed_info(knowledge_base, breed_label):
    """
    RAG: Retrieve breed information from knowledge base
    Uses fuzzy matching to find the best breed match
    """
    breed_label = breed_label.lower().replace('_', ' ')

    # Direct match
    for breed_key, data in knowledge_base.items():
        if any(name in breed_label for name in data["breed_names"]):
            return breed_key, data

    # Partial matching
    for breed_key, data in knowledge_base.items():
        for name in data["breed_names"]:
            if name in breed_label or breed_label in name:
                return breed_key, data

    # Default to general dog care
    return "general_dog", knowledge_base["general_dog"]


# ==================== DATABASE FUNCTIONS ====================

def save_to_db(data):
    """Save pet profile to database"""
    db = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                db = json.load(f)
            except json.JSONDecodeError:
                db = []

    # Add timestamp and unique ID
    data["created_at"] = datetime.now().isoformat()
    data["profile_id"] = str(uuid.uuid4())[:8].upper()

    db.append(data)
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)
    return data["profile_id"]


def load_all_pets():
    """Load all pet profiles"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def update_pet_profile(profile_id, updates):
    """Update existing pet profile"""
    pets = load_all_pets()
    for pet in pets:
        if pet.get("profile_id") == profile_id:
            pet.update(updates)
            pet["last_updated"] = datetime.now().isoformat()
            with open(DB_FILE, "w") as f:
                json.dump(pets, f, indent=4)
            return True
    return False


# ==================== PDF GENERATOR (FIXED) ====================

def create_care_guide_pdf(pet_data, breed_info, breed_display_name):
    """
    Generate personalized care guide PDF
    FIXED: Now correctly uses breed_display_name parameter instead of looking for 'breed' key
    """
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(200, 15, "WOOFER CARE AI - PERSONALIZED GUIDE", ln=True, align='C')
    pdf.ln(5)

    # Pet Info Section
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, f"Pet Profile: {pet_data.get('nickname', 'Unknown')}", ln=True)
    pdf.set_font("Arial", size=11)

    # FIXED: Use the passed breed_display_name parameter instead of breed_info.get('breed')
    pdf.cell(200, 8, f"Breed: {breed_display_name}", ln=True)
    pdf.cell(200, 8, f"Profile ID: {pet_data.get('profile_id', 'N/A')}", ln=True)
    pdf.cell(200, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(5)

    # Nutrition Section
    pdf.set_font("Arial", "B", 13)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(200, 10, " NUTRITION & DIET", ln=True, fill=True)
    pdf.ln(2)

    nutrition = breed_info.get('nutrition', {})
    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, 8, f"Diet Type: {nutrition.get('diet_type', 'N/A')}", ln=True)
    pdf.cell(200, 8, f"Daily Calories: {nutrition.get('calories_per_day', 'N/A')}", ln=True)
    pdf.cell(200, 8, f"Feeding Schedule: {nutrition.get('feeding_schedule', 'N/A')}", ln=True)

    pdf.set_font("Arial", "B", 11)
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

    # Exercise Section
    pdf.set_font("Arial", "B", 13)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(200, 10, " EXERCISE REQUIREMENTS", ln=True, fill=True)
    pdf.ln(2)

    exercise = breed_info.get('exercise', {})
    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, 8, f"Daily Requirement: {exercise.get('daily_requirement', 'N/A')}", ln=True)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, 8, "Recommended Activities:", ln=True)
    pdf.set_font("Arial", size=10)
    for activity in exercise.get('activities', []):
        pdf.cell(200, 6, f"  - {activity}", ln=True)
    pdf.ln(5)

    # Health Section
    pdf.set_font("Arial", "B", 13)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(200, 10, " HEALTH & WELLNESS", ln=True, fill=True)
    pdf.ln(2)

    health = breed_info.get('health', {})
    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, 8, f"Lifespan: {health.get('lifespan', 'N/A')}", ln=True)
    pdf.cell(200, 8, f"Vet Checkups: {health.get('vet_checkups', 'N/A')}", ln=True)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(200, 8, "Common Health Issues to Monitor:", ln=True)
    pdf.set_font("Arial", size=10)
    for issue in health.get('common_issues', []):
        pdf.cell(200, 6, f"  - {issue}", ln=True)
    pdf.ln(5)

    # Supplies Section
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

    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, "Disclaimer: This guide is generated by AI analysis and should be used as general guidance. "
                         "Always consult with a licensed veterinarian for specific medical advice and dietary recommendations "
                         "tailored to your individual pet's needs.")

    return bytes(pdf.output())


# ==================== AI MODEL ====================

@st.cache_resource
def load_woofer_model():
    """Load pre-trained MobileNetV2 for breed identification"""
    return MobileNetV2(weights='imagenet')


def predict_breed(img):
    """
    Predict dog breed from image
    Returns breed name and confidence
    """
    model = load_woofer_model()
    img = img.resize((224, 224))
    x = keras_image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x, verbose=0)
    results = decode_predictions(preds, top=5)[0]

    # Map ImageNet labels to dog breeds (simplified mapping)
    dog_breeds = {
        'siberian_husky': ['siberian_husky', 'eskimo_dog', 'malamute'],
        'golden_retriever': ['golden_retriever'],
        'labrador_retriever': ['labrador_retriever'],
        'german_shepherd': ['german_shepherd', 'malinois'],
        'french_bulldog': ['french_bulldog', 'bulldog'],
        'beagle': ['beagle'],
        'poodle': ['standard_poodle', 'miniature_poodle', 'toy_poodle'],
        'rottweiler': ['rottweiler'],
        'yorkshire_terrier': ['yorkshire_terrier'],
        'boxer': ['boxer'],
        'dachshund': ['dachshund'],
        'pomeranian': ['pomeranian'],
        'chihuahua': ['chihuahua'],
        'border_collie': ['border_collie', 'collie'],
        'shih_tzu': ['shih_tzu'],
        'pug': ['pug'],
        'cocker_spaniel': ['cocker_spaniel', 'english_setter'],
        'doberman': ['doberman'],
        'great_dane': ['great_dane'],
        'schnauzer': ['schnauzer', 'miniature_schnauzer']
    }

    # Check for dog-related predictions
    for imagenet_id, label, confidence in results:
        label_lower = label.lower()

        # Check if it's a dog breed we recognize
        for breed_key, aliases in dog_breeds.items():
            if any(alias in label_lower for alias in aliases):
                return breed_key.replace('_', ' ').title(), confidence

        # General dog detection
        if 'dog' in label_lower or 'hound' in label_lower or 'terrier' in label_lower:
            return label.replace('_', ' ').title(), confidence

    # If no specific dog breed detected, return top result but note uncertainty
    return results[0][1].replace('_', ' ').title(), results[0][2]


# ==================== UI COMPONENTS ====================

def render_header():
    """Render application header"""
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://img.icons8.com/color/96/dog.png", width=80)
    with col2:
        st.title("Woofer Care AI")
        st.markdown("**Intelligent Pet Analysis & Personalized Care Recommendations**")
        st.caption("🐕 Promoting Responsible Pet Ownership Through AI")
    st.markdown("---")


def render_sidebar():
    """Render sidebar with information"""
    with st.sidebar:
        st.header("About Woofer Care AI")
        st.info("""
        **Mission:** Empower pet owners with AI-driven insights for better care.

        **How it works:**
        1. Upload your dog's photo
        2. AI analyzes breed characteristics
        3. Get personalized care recommendations
        4. Track health and supplies

        **Ethical Commitment:**
        - We do not support pet sales or breeding markets
        - Focus on adoption support and welfare
        - Educational resources for responsible ownership
        """)

        st.divider()

        # Statistics
        pets = load_all_pets()
        st.metric("Pets Analyzed", len(pets))

        if pets:
            st.caption(f"Last analysis: {pets[-1].get('created_at', 'N/A')[:10]}")


def render_breed_analysis():
    """Tab 1: AI Breed Analysis & Profile Creation"""
    st.header("🔬 Step 1: AI Breed Analysis")
    st.markdown(
        "Upload your dog's photo to receive instant breed identification and personalized care recommendations.")

    col1, col2 = st.columns([1, 1])

    with col1:
        uploaded_file = st.file_uploader("📸 Upload Dog Photo", type=["jpg", "jpeg", "png"],
                                         help="Clear, well-lit photos work best")

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)

            with st.form("pet_profile_form"):
                st.subheader("Pet Information")
                nickname = st.text_input("Pet Nickname *", placeholder="e.g., Max, Bella",
                                         help="What you call your pet")

                col_age, col_weight = st.columns(2)
                with col_age:
                    age = st.number_input("Age (years)", min_value=0.0, max_value=30.0, value=2.0, step=0.5)
                with col_weight:
                    weight = st.number_input("Weight (kg)", min_value=0.1, max_value=100.0, value=10.0, step=0.5)

                health_notes = st.text_area("Health Notes (Optional)",
                                            placeholder="Any known allergies, conditions, or special needs...")

                submit_button = st.form_submit_button("🔍 Analyze & Create Care Profile", use_container_width=True,
                                                      type="primary")

                if submit_button and nickname:
                    with st.spinner("Analyzing breed characteristics..."):
                        # AI Prediction
                        breed, confidence = predict_breed(image)

                        # Retrieve knowledge base info (RAG)
                        knowledge_base = load_knowledge_base()
                        breed_key, breed_data = get_breed_info(knowledge_base, breed)

                        # Save to database
                        pet_data = {
                            "nickname": nickname,
                            "breed_detected": breed,
                            "ai_confidence": f"{confidence:.1%}",
                            "age": age,
                            "weight": weight,
                            "health_notes": health_notes,
                            "breed_key": breed_key,
                            "care_data": breed_data
                        }
                        profile_id = save_to_db(pet_data)

                        st.session_state['current_pet'] = pet_data
                        st.session_state['analysis_complete'] = True
                        st.success(f"✅ Profile created! ID: {profile_id}")
                        st.rerun()

    with col2:
        if 'analysis_complete' in st.session_state and st.session_state.get('current_pet'):
            pet = st.session_state['current_pet']
            breed_data = pet['care_data']

            st.subheader("📊 Analysis Results")

            # Confidence indicator
            conf_float = float(pet['ai_confidence'].strip('%')) / 100
            st.progress(conf_float, text=f"AI Confidence: {pet['ai_confidence']}")

            # Breed info cards
            st.metric("Detected Breed", pet['breed_detected'])
            st.metric("Estimated Monthly Care Cost", breed_data.get('cost_estimate_monthly', 'N/A'))

            # Quick stats
            st.subheader("Quick Care Stats")
            cols = st.columns(3)
            with cols[0]:
                st.metric("Daily Exercise",
                          breed_data.get('exercise', {}).get('daily_requirement', 'N/A').split()[0] + "h")
            with cols[1]:
                st.metric("Grooming", breed_data.get('grooming', {}).get('brushing', 'N/A').split()[0] + "x/week")
            with cols[2]:
                st.metric("Lifespan", breed_data.get('health', {}).get('lifespan', 'N/A').split()[0] + " yrs")

            # FIXED: Pass the correct breed name to PDF generator
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


def render_care_recommendations():
    """Tab 2: Detailed Care Recommendations"""
    st.header("📋 Step 2: Personalized Care Plan")

    pets = load_all_pets()
    if not pets:
        st.warning("No pet profiles found. Please analyze a pet in Step 1 first.")
        return

    # Pet selector
    selected_pet_name = st.selectbox(
        "Select Pet Profile",
        options=[f"{p['nickname']} ({p['breed_detected']}) - {p['profile_id']}" for p in reversed(pets)],
        index=0
    )

    # Get selected pet data
    selected_profile_id = selected_pet_name.split(" - ")[-1]
    selected_pet = next((p for p in pets if p['profile_id'] == selected_profile_id), None)

    if not selected_pet:
        st.error("Could not load pet data.")
        return

    breed_data = selected_pet.get('care_data', {})

    # Display tabs for different care categories
    care_tabs = st.tabs(["🍖 Nutrition", "🏃 Exercise", "✨ Grooming", "🏥 Health", "🛒 Supplies"])

    with care_tabs[0]:  # Nutrition
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

        # Shopping links for Azerbaijan
        st.divider()
        st.subheader("🛒 Shop in Azerbaijan")
        if nutrition.get('recommended_foods'):
            search_term = nutrition['recommended_foods'][0]  # Use first recommended food as search
            links = get_azerbaijan_search_links(search_term)

            cols = st.columns(3)
            for idx, (store_key, store_info) in enumerate(links.items()):
                with cols[idx]:
                    st.markdown(f"**{store_info['icon']} {store_info['name']}**")
                    st.caption(store_info['description'])
                    st.link_button(f"Search {store_info['name']}", store_info['url'], use_container_width=True)

    with care_tabs[1]:  # Exercise
        st.subheader("Exercise Plan")
        exercise = breed_data.get('exercise', {})

        st.markdown(f"**Daily Requirement:** {exercise.get('daily_requirement', 'N/A')}")

        st.markdown("**🏆 Recommended Activities:**")
        for activity in exercise.get('activities', []):
            st.markdown(f"- {activity}")

        st.markdown("**🧠 Mental Stimulation:**")
        st.markdown(exercise.get('mental_stimulation', 'N/A'))

        # Interactive exercise tracker
        st.divider()
        st.subheader("📅 Daily Exercise Tracker")
        today_exercise = st.number_input("Minutes exercised today", min_value=0, max_value=300, value=30)
        target = 120  # Default target
        if 'hour' in exercise.get('daily_requirement', ''):
            try:
                target = int(exercise['daily_requirement'].split()[0]) * 60
            except:
                pass

        progress = min(today_exercise / target, 1.0)
        st.progress(progress, text=f"{today_exercise}/{target} minutes ({progress:.0%})")

        if progress >= 1.0:
            st.success("🎉 Daily exercise goal achieved!")
        else:
            st.info(f"💪 {target - today_exercise} more minutes to reach today's goal")

    with care_tabs[2]:  # Grooming
        st.subheader("Grooming Schedule")
        grooming = breed_data.get('grooming', {})

        cols = st.columns(3)
        with cols[0]:
            st.metric("Brushing Frequency", grooming.get('brushing', 'N/A'))
        with cols[1]:
            st.metric("Bathing", grooming.get('bathing', 'N/A'))
        with cols[2]:
            st.metric("Nail Trimming", grooming.get('nail_trimming', 'N/A'))

        st.info(f"**Special Notes:** {grooming.get('special_notes', 'N/A')}")

        # Grooming checklist
        st.divider()
        st.subheader("✅ This Week's Grooming Checklist")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.checkbox("Brushing Session")
        with c2:
            st.checkbox("Nail Check")
        with c3:
            st.checkbox("Ear Cleaning")

    with care_tabs[3]:  # Health
        st.subheader("Health Monitoring")
        health = breed_data.get('health', {})

        st.markdown(f"**Expected Lifespan:** {health.get('lifespan', 'N/A')}")
        st.markdown(f"**Recommended Vet Visits:** {health.get('vet_checkups', 'N/A')}")

        st.markdown("**⚠️ Common Health Issues to Monitor:**")
        for issue in health.get('common_issues', []):
            st.markdown(f"- {issue}")

        # Health records section
        st.divider()
        st.subheader("🏥 Health Records")

        vet_date = st.date_input("Last Vet Visit", value=datetime.now() - timedelta(days=30))
        next_due = st.date_input("Next Appointment Due", value=datetime.now() + timedelta(days=60))

        days_until = (next_due - datetime.now().date()).days
        if days_until < 7:
            st.error(f"⚠️ Vet appointment due in {days_until} days!")
        elif days_until < 30:
            st.warning(f"⏰ Vet appointment coming up in {days_until} days")
        else:
            st.success(f"✅ Next checkup in {days_until} days")

        if selected_pet.get('health_notes'):
            st.info(f"**Your Notes:** {selected_pet['health_notes']}")

    with care_tabs[4]:  # Supplies
        st.subheader("Recommended Supplies")

        for category in breed_data.get('supplies', []):
            with st.expander(f"📦 {category['category']}"):
                for item in category['items']:
                    cols = st.columns([3, 1])
                    with cols[0]:
                        st.markdown(f"- **{item}**")
                    with cols[1]:
                        # FIXED: Create search links for this specific item
                        links = get_azerbaijan_search_links(item)

                        # Create a dropdown for store selection
                        store_options = {f"{v['icon']} {v['name']}": v['url'] for k, v in links.items()}
                        selected_store = st.selectbox(
                            "Choose store",
                            options=list(store_options.keys()),
                            key=f"store_select_{category['category']}_{item}",
                            label_visibility="collapsed"
                        )

                        if selected_store:
                            st.link_button("🛒 Buy Now", store_options[selected_store], use_container_width=True)

        st.divider()
        st.caption(
            "**Note:** Product recommendations are based on breed-specific needs. We may earn a small commission from affiliate links, which supports our mission of promoting responsible pet care.")


def render_health_tracker():
    """Tab 3: Health & Wellness Tracking"""
    st.header("🏥 Health & Wellness Tracker")

    pets = load_all_pets()
    if not pets:
        st.warning("No pets registered yet. Please create a profile in Step 1.")
        return

    # Overview metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pets Tracked", len(pets))
    with col2:
        avg_age = sum(p.get('age', 0) for p in pets) / len(pets) if pets else 0
        st.metric("Average Age", f"{avg_age:.1f} years")
    with col3:
        st.metric("Care Guides Generated", len(pets))

    # Pet health dashboard
    st.subheader("Your Pets' Health Overview")

    for pet in reversed(pets[-5:]):  # Show last 5 pets
        with st.expander(f"🐕 {pet['nickname']} ({pet['breed_detected']})"):
            cols = st.columns([2, 2, 1])
            with cols[0]:
                st.markdown(f"**Age:** {pet.get('age', 'N/A')} years")
                st.markdown(f"**Weight:** {pet.get('weight', 'N/A')} kg")
            with cols[1]:
                created_date = datetime.fromisoformat(pet.get('created_at', datetime.now().isoformat()))
                days_since = (datetime.now() - created_date).days
                st.markdown(f"**Profile Age:** {days_since} days")
                st.markdown(f"**AI Confidence:** {pet.get('ai_confidence', 'N/A')}")
            with cols[2]:
                if st.button("View Details", key=f"view_{pet['profile_id']}"):
                    st.session_state['selected_pet_id'] = pet['profile_id']
                    st.rerun()

    # Reminders section
    st.divider()
    st.subheader("⏰ Care Reminders")

    reminder_type = st.selectbox("Set New Reminder",
                                 ["Vet Appointment", "Vaccination", "Grooming", "Medication", "Buy Food"])
    reminder_date = st.date_input("Reminder Date", min_value=datetime.now().date())
    reminder_note = st.text_input("Notes")

    if st.button("Add Reminder"):
        st.success(f"✅ Reminder set: {reminder_type} on {reminder_date}")
        # In a full app, this would save to a reminders database


def render_adoption_support():
    """Tab 4: Adoption & Welfare Resources"""
    st.header("🏠 Adoption & Welfare Support")

    st.markdown("""
    ### Our Ethical Stance
    At Woofer Care AI, we believe every pet deserves a loving home. We do not support commercial breeding 
    or pet sales. Instead, we focus on:
    - Supporting adopters with AI-powered care guidance
    - Promoting responsible ownership
    - Connecting owners with welfare resources
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🐾 Why Adopt?")
        st.markdown("""
        - **Save a Life:** Millions of healthy pets are euthanized yearly due to overcrowding
        - **Combat Puppy Mills:** Adoption doesn't support cruel breeding operations
        - **Adult Pets Available:** Skip the destructive puppy phase
        - **Cost Effective:** Adoption fees include vaccinations and spaying/neutering
        """)

        st.subheader("📚 Pre-Adoption Checklist")
        checklist_items = [
            "Research breed-specific needs (use our AI tool!)",
            "Calculate monthly costs (food, vet, supplies)",
            "Ensure your housing allows pets",
            "Plan for exercise and socialization time",
            "Find a local veterinarian",
            "Pet-proof your home"
        ]
        for item in checklist_items:
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

        *Note: These are example listings. Research local options in your area.*
        """)

        st.subheader("💝 How to Help")
        st.markdown("""
        - **Foster:** Temporarily house pets waiting for homes
        - **Volunteer:** Help at local shelters
        - **Donate:** Support welfare organizations
        - **Educate:** Share responsible ownership knowledge
        """)

    st.divider()
    # FIXED: Simplified footer text
    st.caption("Contact us!")


# ==================== MAIN APPLICATION ====================

def main():
    # Initialize knowledge base if needed
    if not os.path.exists(KNOWLEDGE_BASE_FILE):
        initialize_knowledge_base()

    render_header()
    render_sidebar()

    # Main navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔬 AI Analysis",
        "📋 Care Plan",
        "🏥 Health Tracker",
        "🏠 Adoption Support"
    ])

    with tab1:
        render_breed_analysis()

    with tab2:
        render_care_recommendations()

    with tab3:
        render_health_tracker()

    with tab4:
        render_adoption_support()

    # Footer
    st.markdown("---")
    st.caption("""
    **Woofer Care AI** | Promoting Responsible Pet Ownership through Technology | 
    © 2025 Woofer Project | Not for use in pet sales or breeding markets
    """)


if __name__ == "__main__":

    main()


