import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="FARINEA Master AI", page_icon="💎", layout="centered")

st.markdown("<h2 style='text-align: center;'>💎 FARINEA Master AI Agent</h2>", unsafe_allow_html=True)
st.write("---")

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
GMAIL_USER = st.secrets.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = st.secrets.get("GMAIL_APP_PASSWORD", "")
SHEET_URL = st.secrets.get("SHEET_URL", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.warning("Gemini API Key add kijiye settings me.")

MODEL_NAME = "gemini-3.8-flash"

def speak_text(text):
    clean_text = text.replace("\n", " ").replace('"', "'")
    audio_html = f"""
    <script>
    let utterance = new SpeechSynthesisUtterance("{clean_text}");
    utterance.lang = 'hi-IN';
    window.speechSynthesis.speak(utterance);
    </script>
    """
    st.components.v1.html(audio_html, height=0)

def get_sheet_summary():
    if not SHEET_URL:
        return "Google Sheet link abhi set nahi hai. Normal checklist data ready hai."
    try:
        # Sheet link ko CSV format me convert karke live rows read karna
        if "/edit" in SHEET_URL:
            csv_url = SHEET_URL.split("/edit")[0] + "/export?format=csv"
        else:
            csv_url = SHEET_URL
        df = pd.read_csv(csv_url)
        summary = f"Total Items/Rows: {len(df)}\nColumns: {', '.join(df.columns)}\nTop Data Preview:\n{df.head(5).to_string(index=False)}"
        return summary
    except Exception as e:
        return f"Sheet load error: {e}"

def send_real_email(subject, body):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return False, "Secrets me GMAIL_USER aur GMAIL_APP_PASSWORD add kijiye."
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, f"Report successfully sent to {GMAIL_USER}!"
    except Exception as e:
        return False, str(e)

# 1. Voice Host & Morning Briefing (Google Sheet Linked)
st.subheader("🗣️ Business Briefing & Voice Host")
if st.button("🎙 Daily Morning Briefing", use_container_width=True):
    if GEMINI_API_KEY:
        try:
            with st.spinner("Google Sheet se live data lekar briefing ban rahi hai..."):
                sheet_data = get_sheet_summary()
                model = genai.GenerativeModel(MODEL_NAME)
                prompt = f"""
                Aap FARINEA Jewellery brand ke executive AI business partner hain.
                Neeche diye Google Sheet ke live data ko dhyan se dekhiye aur meeting host ki tarah 3-4 clear Hindi sentences me professional morning briefing boliye:
                
                Live Sheet Data:
                {sheet_data}
                
                Stock, orders aur priority par baat karein.
                """
                response = model.generate_content(prompt)
                st.session_state['last_briefing'] = response.text
                st.session_state['sheet_data'] = sheet_data
                st.success(response.text)
                speak_text(response.text)
        except Exception as e:
            st.error(f"Error: {e}")

# 2. Voice Input / Direct Baat Karein
st.write("---")
st.subheader("🎙️ FARINEA Voice Assistant (Direct Baat Karein)")
st.caption("Aap keyboard mic se bolkar ya type karke sawaal pooch sakte hain.")
user_query = st.chat_input("Google Sheet ya business ke baare me sawaal poochein...")

if user_query:
    if GEMINI_API_KEY:
        try:
            with st.spinner("Sheet data check ho raha hai..."):
                sheet_data = get_sheet_summary()
                model = genai.GenerativeModel(MODEL_NAME)
                chat_prompt = f"""
                User question: {user_query}
                Aapke paas FARINEA ki Google Sheet ka data ye hai:
                {sheet_data}
                
                Is data ke aadhar par user ko Hindi me short aur seedha jawab dijiye.
                """
                ans = model.generate_content(chat_prompt)
                st.write(f"**Aap:** {user_query}")
                st.success(f"**FARINEA AI:** {ans.text}")
                speak_text(ans.text)
        except Exception as e:
            st.error(f"Error: {e}")

# 3. Meesho Studio
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
                    model = genai.GenerativeModel(MODEL_NAME)
                    prompt = f"""
                    Is jewellery photo ko analyse karke Meesho listing ready kijiye:
                    1. Product Title
                    2. Recommended Selling Price (Cost Rs {cost_price}, 40-50% margin)
                    3. Key Highlights
                    4. Description
                    5. Top 10 Meesho Keywords
                    """
                    response = model.generate_content([prompt, image])
                    st.text_area("📋 Meesho Ready Content", value=response.text, height=250)
                except Exception as e:
                    st.error(f"Error: {e}")

# 4. Email Operations
st.write("---")
st.subheader("📊 Operations & Daily Report")
if st.button("📤 Send Today's Report to Gmail", use_container_width=True):
    briefing_content = st.session_state.get('last_briefing', 'Aaj ka daily stock summary ready hai.')
    sheet_data = st.session_state.get('sheet_data', get_sheet_summary())
    email_body = f"FARINEA Master AI Daily Summary Report:\n\n{briefing_content}\n\n-- Live Data Reference --\n{sheet_data}\n\nGenerated automatically for FARINEA Jewellery."
    success, msg = send_real_email("FARINEA Daily Business Report", email_body)
    if success:
        st.success(f"✅ {msg}")
    else:
        st.error(f"❌ {msg}")
