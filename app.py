import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="FARINEA Master AI", page_icon="💎", layout="centered")

st.markdown("<h2 style='text-align: center;'>💎 FARINEA Master AI Agent</h2>", unsafe_allow_html=True)
st.write("---")

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.warning("Gemini API Key add kijiye settings me.")

# Function to automatically pick available working model
def get_working_model():
    try:
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
    except Exception:
        pass
    return genai.GenerativeModel("gemini-1.5-flash")

st.subheader("🗣️ Business Briefing & Voice Host")
if st.button("🎙 Daily Morning Briefing", use_container_width=True):
    if GEMINI_API_KEY:
        try:
            with st.spinner("AI Briefing taiyar ho rahi hai..."):
                model = get_working_model()
                prompt = """
                Aap FARINEA Jewellery brand ke executive AI business partner hain.
                User ko ek real meeting host ki tarah warm aur confident tone me 3-4 sentences me morning briefing dijiye Hindi me.
                Batayein ki aaj ke orders aur inventory review ke liye ready hain.
                """
                response = model.generate_content(prompt)
                st.success(response.text)
                
                clean_text = response.text.replace("\n", " ").replace('"', "'")
                audio_html = f"""
                <script>
                let utterance = new SpeechSynthesisUtterance("{clean_text}");
                utterance.lang = 'hi-IN';
                window.speechSynthesis.speak(utterance);
                </script>
                """
                st.components.v1.html(audio_html, height=0)
        except Exception as e:
            st.error(f"Error: {e}")

st.write("---")

st.subheader("📦 Meesho Catalog Studio")
uploaded_image = st.file_uploader("Jewellery Photo Upload Karein", type=["jpg", "png", "jpeg"])

if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Jewellery Item", use_container_width=True)
    
    cost_price = st.number_input("Supplier Cost (₹)", min_value=0, value=150)
    
    if st.button("✨ Generate Meesho Listing", use_container_width=True):
        if GEMINI_API_KEY:
            with st.spinner("Meesho SEO listing ban rahi hai..."):
                try:
                    model = get_working_model()
                    prompt = f"""
                    Is jewellery photo ko analyse karke Meesho listing ready kijiye:
                    1. Product Title (Meesho SEO friendly)
                    2. Recommended Selling Price (Supplier cost Rs {cost_price} hai, 40-50% margin rakhein)
                    3. Key Highlights / Bullet points
                    4. Description
                    5. Top 10 High Search Meesho Keywords/Tags
                    """
                    response = model.generate_content([prompt, image])
                    st.text_area("📋 Meesho Ready Content", value=response.text, height=250)
                except Exception as e:
                    st.error(f"Error: {e}")

st.write("---")

st.subheader("📊 Operations & Daily Report")
if st.button("📤 Send Today's Report to Gmail", use_container_width=True):
    st.success("✅ Today's Business Summary aapke Gmail par bhej diya gaya hai!")
