import streamlit as st
from groq import Groq
from datetime import date
import requests
import time
import base64
import os

GROQ_KEY = os.environ.get("GROQ_KEY", "")
WEATHER_KEY = os.environ.get("WEATHER_KEY", "")

client = Groq(api_key=GROQ_KEY)

st.markdown("""
<style>
* { color: #3a2a0a !important; }
.stApp { background: #f5f0e8 !important; }
.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #8B6914;
    padding: 12px 20px;
    border-radius: 15px;
    margin-bottom: 15px;
}
.top-bar * { color: white !important; }
.kisan-naam { font-size: 17px; font-weight: bold; }
.dukaan-naam {
    font-size: 12px;
    background: rgba(255,255,255,0.2);
    padding: 5px 10px;
    border-radius: 8px;
    text-align: right;
}
.card {
    background: #fff8e1;
    border-radius: 15px;
    padding: 15px;
    margin: 8px 0;
    border: 1px solid #c8a96e;
}
.weather-card {
    background: #fff8e1;
    border-radius: 15px;
    padding: 15px;
    margin: 8px 0;
    border: 1px solid #c8a96e;
    text-align: center;
}
.stage-card {
    background: #fff8e1;
    border-radius: 15px;
    padding: 15px;
    margin: 8px 0;
    border-left: 5px solid #2d8a2d;
}
.advice-card {
    background: #fff8e1;
    border-radius: 15px;
    padding: 15px;
    margin: 8px 0;
    border-left: 5px solid #8B6914;
}
.splash {
    text-align: center;
    padding: 40px;
    background: #fff8e1;
    border-radius: 20px;
    border: 2px solid #c8a96e;
}
.fasal-area {
    text-align: center;
    padding: 20px;
    background: #fff8e1;
    border-radius: 15px;
    border: 2px solid #c8a96e;
    margin: 8px 0;
}
.greetings {
    text-align: center;
    font-size: 12px;
    padding: 10px;
    border-top: 2px solid #c8a96e;
    margin-top: 15px;
    background: #fff8e1;
    border-radius: 10px;
    color: #8B6914 !important;
}
.camera-card {
    background: #fff8e1;
    border-radius: 15px;
    padding: 15px;
    margin: 8px 0;
    border: 2px dashed #2d8a2d;
    text-align: center;
}
.stButton > button {
    background: #8B6914 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: bold !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #5a3e10 !important;
}
.stTextInput > div > div > input {
    background: #fff8e1 !important;
    border: 2px solid #c8a96e !important;
    border-radius: 10px !important;
    color: #3a2a0a !important;
}
.stSelectbox > div > div {
    background: #fff8e1 !important;
    border: 2px solid #c8a96e !important;
    border-radius: 10px !important;
    color: #3a2a0a !important;
}
.stDateInput > div > div > input {
    background: #fff8e1 !important;
    border: 2px solid #c8a96e !important;
    border-radius: 10px !important;
    color: #3a2a0a !important;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize
if "messages" not in st.session_state:
    st.session_state.messages = []
if "kisan_naam" not in st.session_state:
    st.session_state.kisan_naam = ""
if "naam_liya" not in st.session_state:
    st.session_state.naam_liya = False
if "fasal" not in st.session_state:
    st.session_state.fasal = ""
if "beej_date" not in st.session_state:
    st.session_state.beej_date = None
if "shehar" not in st.session_state:
    st.session_state.shehar = ""
if "splash_done" not in st.session_state:
    st.session_state.splash_done = False
if "show_address" not in st.session_state:
    st.session_state.show_address = False

# Functions
def get_fasal_visual(fasal, din):
    if fasal == "🌾 Chawal (Rice)":
        if din <= 25: return "🌱", "Nursery"
        elif din <= 50: return "🌿", "Transplanting"
        elif din <= 80: return "🌾", "Growth"
        elif din <= 110: return "🌸", "Flowering"
        else: return "✂️", "Harvesting"
    elif fasal == "🌿 Gehun (Wheat)":
        if din <= 21: return "🌱", "Jamav"
        elif din <= 45: return "🌿", "Tillering"
        elif din <= 75: return "🌾", "Growth"
        elif din <= 110: return "🌸", "Bali"
        else: return "✂️", "Harvesting"
    elif fasal == "🟡 Sarso (Mustard)":
        if din <= 20: return "🌱", "Jamav"
        elif din <= 45: return "🌿", "Growth"
        elif din <= 75: return "🌸", "Phool"
        else: return "✂️", "Harvesting"
    elif fasal == "🍬 Ganna (Sugarcane)":
        if din <= 30: return "🌱", "Jamav"
        elif din <= 90: return "🌿", "Growth"
        elif din <= 180: return "🎋", "Bhadai"
        elif din <= 270: return "🍬", "Ripening"
        else: return "✂️", "Harvesting"
    return "🌱", "Unknown"

def get_weather(shehar):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={shehar}&appid={WEATHER_KEY}&units=metric&lang=hi"
        r = requests.get(url)
        data = r.json()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"]
        wind = data["wind"]["speed"]
        weather_id = data["weather"][0]["id"]
        if weather_id < 300: icon = "⛈️"
        elif weather_id < 600: icon = "🌧️"
        elif weather_id < 700: icon = "❄️"
        elif weather_id < 800: icon = "🌫️"
        elif weather_id == 800: icon = "☀️"
        else: icon = "⛅"
        return {"icon": icon, "temp": temp, "humidity": humidity,
                "description": description, "wind": wind}
    except:
        return None

def fasal_season_check(fasal, beej_date):
    month = beej_date.month
    warnings = {
        "🌾 Chawal (Rice)": {"sahi_mahine": [5,6,7], "message": "⚠️ Chawal ka sahi samay June-July hai! Abhi risk hai."},
        "🌿 Gehun (Wheat)": {"sahi_mahine": [10,11,12], "message": "⚠️ Gehun ka sahi samay October-December hai!"},
        "🟡 Sarso (Mustard)": {"sahi_mahine": [9,10,11], "message": "⚠️ Sarso ka sahi samay September-November hai!"}
        "🍬 Ganna (Sugarcane)": {"sahi_mahine": [2, 3, 4, 10, 11],"message": "⚠️ Ganne ki fasal ka sahi samay February-April ya October-November hai!"},
    }
    if fasal in warnings:
        if month not in warnings[fasal]["sahi_mahine"]:
            return warnings[fasal]["message"]
    return None

def fasal_stage(fasal, beej_date):
    din = (date.today() - beej_date).days
    if fasal == "🌾 Chawal (Rice)":
        if din <= 25: return f"🌱 Nursery Stage (Din {din}/25)", "Roz paani do. Peele patte dikhein to Zinc Sulphate spray karo"
        elif din <= 50: return f"🌿 Transplanting Stage (Din {din}/50)", "Khet mein 2-3 inch paani rakho"
        elif din <= 80: return f"🌾 Growth Stage (Din {din}/80)", "Urea khad daalo — 25kg per acre"
        elif din <= 110: return f"🌸 Flowering Stage (Din {din}/110)", "Paani mat rokna — bahut zaroori hai"
        else: return f"✂️ Harvesting Stage (Din {din})", "Fasal taiyaar — paani band karo"
    elif fasal == "🌿 Gehun (Wheat)":
        if din <= 21: return f"🌱 Jamav Stage (Din {din}/21)", "Pehla paani do"
        elif din <= 45: return f"🌿 Tillering Stage (Din {din}/45)", "Urea daalo — 30kg per acre"
        elif din <= 75: return f"🌾 Growth Stage (Din {din}/75)", "Doosra paani do aur potash daalo"
        elif din <= 110: return f"🌸 Bali Stage (Din {din}/110)", "Teesra paani do"
        else: return f"✂️ Harvesting Stage (Din {din})", "Gehun taiyaar — combine harvester book karo"
    elif fasal == "🟡 Sarso (Mustard)":
        if din <= 20: return f"🌱 Jamav Stage (Din {din}/20)", "Halka paani do"
        elif din <= 45: return f"🌿 Growth Stage (Din {din}/45)", "Urea aur keeton ki dawai spray karo"
        elif din <= 75: return f"🌸 Phool Stage (Din {din}/75)", "Koi spray mat karo"
        else: return f"✂️ Harvesting Stage (Din {din})", "Sarso katne ka samay!"
    elif fasal == "🍬 Ganna (Sugarcane)":
        if din <= 30:
        return f"🌱 Jamav Stage (Din {din}/30)", "Halka paani do — roz check karo"
        elif din <= 90:
        return f"🌿 Growth Stage (Din {din}/90)", "Urea daalo — 50kg per acre — paani regular rakho"
        elif din <= 180:
        return f"🎋 Bhadai Stage (Din {din}/180)", "Potash daalo — 25kg per acre — tying karo"
        elif din <= 270:
        return f"🍬 Ripening Stage (Din {din}/270)", "Paani kam karo — koi khad mat daalo"
        else:
        return f"✂️ Harvesting Stage (Din {din})", "Ganna katne ka samay — mill se contact karo"
    return "Stage pata nahi", "Sahi fasal chunein"

def analyze_image(image_bytes, fasal):
    try:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        response = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                    {"type": "text", "text": f"Ye {fasal} fasal ki photo hai. Hindi mein sirf 3 lines mein batao: kya problem hai aur kya karna chahiye?"}
                ]
            }],
            max_tokens=200
        )
        return response.choices[0].message.content
    except:
        return "Photo analysis nahi ho saki — dobara try karo!"

# ===== SPLASH =====
if not st.session_state.splash_done:
    st.markdown("""
    <div class='splash'>
        <div style='font-size:80px'>🌾</div>
        <h1 style='color:#8B6914 !important; font-size:36px'>Kisan Saathi</h1>
        <h3 style='color:#5a3e10 !important'>Hanuman Khad Bhandar</h3>
        <p style='color:#8B6914 !important'>Vill. Hatt (Safidon), Jind</p>
        <p style='color:#2d8a2d !important'>Loading...</p>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2)
    st.session_state.splash_done = True
    st.rerun()

# ===== NAAM SCREEN =====
elif not st.session_state.naam_liya:
    st.markdown("""
    <div class='splash'>
        <div style='font-size:60px'>🙏</div>
        <h2 style='color:#8B6914 !important'>Namaste!</h2>
        <p style='color:#5a3e10 !important'>Main aapka Kisan Saathi hoon</p>
        <p style='color:#8B6914 !important'>— Hanuman Khad Bhandar ki taraf se —</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    naam = st.text_input("📝 Apna naam likhein:", placeholder="Jaise: Ramesh Kumar")
    shehar = st.text_input("📍 Apna shehar/gaon likhein:", placeholder="Jaise: Safidon, Jind")
    if st.button("✅ Aage Badho"):
        if naam.strip() == "":
            st.warning("Kripya apna naam likhein!")
        elif shehar.strip() == "":
            st.warning("Kripya apna shehar likhein!")
        else:
            st.session_state.kisan_naam = naam
            st.session_state.shehar = shehar
            st.session_state.naam_liya = True
            st.rerun()

# ===== FASAL SCREEN =====
elif st.session_state.fasal == "":
    st.markdown(f"""
    <div class='splash'>
        <div style='font-size:50px'>🌾</div>
        <h3 style='color:#8B6914 !important'>Namaste {st.session_state.kisan_naam} ji!</h3>
        <p style='color:#5a3e10 !important'>Aap kaunsi fasal uga rahe hain?</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    fasal = st.selectbox("🌱 Fasal chunein:", [
        "🌾 Chawal (Rice)", "🌿 Gehun (Wheat)", "🟡 Sarso (Mustard)", "🍬 Ganna (Sugarcane)"])
    beej_date = st.date_input("📅 Beej kab boya tha?", max_value=date.today())
    if st.button("🚀 Tracking Shuru Karein"):
        warning = fasal_season_check(fasal, beej_date)
        st.session_state.fasal = fasal
        st.session_state.beej_date = beej_date
        if warning:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"{st.session_state.kisan_naam} ji, {warning} Phir bhi main madad karunga! 🙏"
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Namaste {st.session_state.kisan_naam} ji! 🙏 Aapki {fasal} fasal ka track shuru ho gaya!"
            })
        st.rerun()

# ===== MAIN APP =====
else:
    stage, advice = fasal_stage(st.session_state.fasal, st.session_state.beej_date)
    din = (date.today() - st.session_state.beej_date).days
    fasal_icon, fasal_stage_name = get_fasal_visual(st.session_state.fasal, din)
    weather = get_weather(st.session_state.shehar)

    # Top Bar
    st.markdown(f"""
    <div class='top-bar'>
        <div class='kisan-naam'>🙏 Namaste, {st.session_state.kisan_naam} ji!</div>
        <div class='dukaan-naam'>🏪 Hanuman Khad Bhandar<br><small>Vill. Hatt (Safidon)</small></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📍 Dukaan Ka Address"):
        st.session_state.show_address = not st.session_state.show_address
    if st.session_state.show_address:
        st.markdown("""
        <div class='card'>
            <h4 style='color:#8B6914 !important'>📍 Hanuman Khad Bhandar</h4>
            <p>Vill. Hatt (Safidon), Jind, Haryana</p>
            <p>🌾 Khad, Beej aur Dawaiyan uplabdh hain</p>
        </div>
        """, unsafe_allow_html=True)

    if weather:
        st.markdown(f"""
        <div class='weather-card'>
            <h3>{weather['icon']} {st.session_state.shehar} ka Mausam</h3>
            <h2 style='color:#8B6914 !important'>{weather['temp']}°C</h2>
            <p>{weather['description']}</p>
            <p>💧 Naami: {weather['humidity']}% | 💨 Hawa: {weather['wind']} m/s</p>
            <p style='color:#8B6914 !important; font-size:11px'>⚠️ Mausam approximate hai — 3-5 degree ka fark normal hai</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='fasal-area'>
        <div style='font-size:90px'>{fasal_icon}</div>
        <h3 style='color:#2d8a2d !important'>{st.session_state.fasal}</h3>
        <p style='color:#5a3e10 !important'>Din {din} — {fasal_stage_name} Stage</p>
    </div>
    <div class='stage-card'>
        <h4 style='color:#2d8a2d !important'>🌱 Abhi Ki Stage</h4>
        <p>{stage}</p>
    </div>
    <div class='advice-card'>
        <h4 style='color:#8B6914 !important'>💡 Abhi Kya Karein</h4>
        <p>{advice}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class='camera-card'>
        <h4 style='color:#2d8a2d !important'>📸 Fasal Ki Photo Khicho</h4>
        <p>Photo se AI bimaari pakad lega!</p>
    </div>
    """, unsafe_allow_html=True)

    camera_photo = st.camera_input("📷 Camera se photo lo")
    if camera_photo:
        with st.spinner("Photo dekh raha hoon..."):
            result = analyze_image(camera_photo.getvalue(), st.session_state.fasal)
            st.markdown(f"""
            <div class='card'>
                <h4 style='color:#2d8a2d !important'>🔍 Photo Analysis</h4>
                <p>{result}</p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Photo analysis: {result}"
            })

    st.markdown("---")
    st.markdown("### 🤖 Kisan Saathi se Poochho")
    st.info("💡 Apna sawaal neeche likhein!")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    question = st.chat_input("Apna sawaal likhein...")

    if question:
        st.chat_message("user").write(question)
        st.session_state.messages.append({"role": "user", "content": question})

        with st.spinner("Soch raha hoon..."):
            weather_info = f"{weather['temp']}°C, {weather['description']}" if weather else "Uplabdh nahi"
            chat_history = [{"role": "system", "content": f"""Tu ek experienced Indian agriculture expert hai.
Kisan ka naam: {st.session_state.kisan_naam}
Shehar: {st.session_state.shehar}
Fasal: {st.session_state.fasal}
Stage: {stage}
Mausam: {weather_info}
Rules:
- Hamesha Hindi mein jawab de
- Sirf 2-3 lines mein jawab do agar possible hai to
- Aasan bhasha
- Seedha solution batao
- Kisan jo baat bataye usse seedha samjho — ulta mat samjho
- Agar kisan koi information share kare to sirf acknowledge karo — unnecessary advice mat do
- Sirf tab dawai batao jab kisan pooche
- Kisan ki baat ka seedha jawab do — topic mat badlo
- Bullet points kam use karo — seedhi baat karo
- agar koi dawai ke liye dukan ke baare mai puche to Hanuman khad Bhandar ke baare mai batao uske baare mai achi cheeje batakar uski location batao , dukan ki location Hatt(safidon) district jind
- Think step by step. First identify the disease, then suggest treatment, then give precautions
- Answer in 3 bullet points only. Use simple language a farmer can understand
- dawai ka naam batane ki bajaye dawai ka salt batao 
- jawab dene se pehle apne jawab ki jaanch karo
- Never suggest a medicine combination that is harmful or can damage crops.
- If two medicines are incompatible, clearly warn: "⚠️ Yeh dono ek saath mat milana"
- If you are not confident about a diagnosis, honestly say: 
  "Mujhe puri tarah bimaari samajh nahi aayi, kripya ek krishi expert se milein , ya iski or jaankari de."
- Never guess a disease just to give an answer.
- agar kisan ki fasal mai koi bimaari hai to usse sawal puch sakte ho taaki pata chal sake ki bimaari kya par jawab hamesha sahi do
- Dawai ka salt aur matra batao"""}] + st.session_state.messages

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=chat_history,
                max_tokens=150
            )
            jawab = response.choices[0].message.content

        st.chat_message("assistant").write(jawab)
        st.session_state.messages.append({"role": "assistant", "content": jawab})
        st.rerun()

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Nayi Fasal"):
            st.session_state.fasal = ""
            st.session_state.beej_date = None
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("🔄 Weather Update"):
            st.rerun()

    st.markdown("""
    <div class='greetings'>
        🌾 Greetings from Hanuman Khad Bhandar, Vill. Hatt (Safidon) 🌾<br>
        <small>⚠️ Ye salah sirf margdarshan ke liye hai — dawai se pehle expert se milein</small>
    </div>
    """, unsafe_allow_html=True)