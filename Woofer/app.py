import streamlit as st
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image as keras_image
import numpy as np
from PIL import Image
import time
import uuid
import json
import os
from fpdf import FPDF

# Naming for the UI
st.set_page_config(page_title="Woofer AI & Fintech Project", page_icon="🐶")

DB_FILE = "woofer_registry.json"

# Database
def save_to_db(data):
    db = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                db = json.load(f)
            except json.JSONDecodeError:
                db = []
    db.append(data)
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)


def load_all_dogs():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


# Pdf generator
def create_pdf_receipt(receipt_id, dog_name, breed, amount, token):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "WOOFER - OFFICIAL ESCROW RECEIPT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Receipt ID: {receipt_id}", ln=True)
    pdf.cell(200, 10, f"Dog Name: {dog_name}", ln=True)
    pdf.cell(200, 10, f"Verified Breed: {breed}", ln=True)
    pdf.cell(200, 10, f"Identity Token: {token}", ln=True)
    pdf.cell(200, 10, f"Escrow Amount: {amount} AZN", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "This document confirms that funds are held in Woofer's Secure Escrow. "
                          "The transaction is protected by AI-Identity verification.")
    return pdf.output(dest='S').encode('latin-1')


# AI Model
@st.cache_resource
def load_woofer_model():
    return MobileNetV2(weights='imagenet')


model = load_woofer_model()


def predict_breed(img):
    img = img.resize((224, 224))
    x = keras_image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    results = decode_predictions(preds, top=3)[0]
    for _, label, confidence in results:
        if "husky" in label.lower() or "eskimo_dog" in label.lower():
            return "Siberian Husky", confidence
    return results[0][1].replace('_', ' ').title(), results[0][2]


# UI
st.title("🐶 Woofer: AI X Fintech")
st.markdown("---")

tab1, tab2 = st.tabs(["🛡️ Verification", "💰 Escrow Marketplace"])

with tab1:
    st.header("Step 1: AI Dog Identity")
    uploaded_file = st.file_uploader("Upload Pet Photo", type=["jpg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        dog_nick = st.text_input("Give this dog a nickname (for the database)", value="Buddy")

        if st.button("Analyze and Generate Identity Token"):
            breed, conf = predict_breed(image)
            token = str(uuid.uuid4())[:8].upper()

            pet_data = {
                "nickname": dog_nick,
                "token": token,
                "breed": breed,
                "confidence": f"{conf:.2%}",
                "timestamp": time.ctime()
            }
            save_to_db(pet_data)
            st.success(f"Verified {breed}! Dog '{dog_nick}' added to registry.")

with tab2:
    st.header("Step 2: Secure Escrow Payment")

    # here we all dogs from JSON for the selection box
    all_dogs = load_all_dogs()

    if not all_dogs:
        st.warning("The registry is empty. Please verify dogs in Tab 1 first.")
    else:
        # and create a list of labels for the dropdown in the format of "Nickname (Breed)"
        dog_options = [f"{d['nickname']} ({d['breed']})" for d in all_dogs]
        selected_index = st.selectbox("Select a dog from the Verified Registry:", range(len(dog_options)),
                                      format_func=lambda x: dog_options[x])

        selected_dog = all_dogs[selected_index]

        st.info(f"**Target Dog:** {selected_dog['nickname']} | **Token:** {selected_dog['token']}")

        amount = st.number_input("Transaction Amount (AZN)", min_value=1, value=250)

        if st.button("Lock Funds in Escrow"):
            receipt_id = f"WFR-{uuid.uuid4().hex[:6].upper()}"
            pdf_bytes = create_pdf_receipt(
                receipt_id,
                selected_dog['nickname'],
                selected_dog['breed'],
                amount,
                selected_dog['token']
            )

            st.success(f"✅ Transaction for {selected_dog['nickname']} Secured!")
            st.download_button(
                label="📥 Download Official PDF Receipt",
                data=pdf_bytes,
                file_name=f"Woofer_Receipt_{selected_dog['nickname']}.pdf",
                mime="application/pdf"
            )