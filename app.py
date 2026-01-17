# To run this, you would need a file named app.py
import streamlit as st
import random
from gtts import gTTS
from io import BytesIO
import pandas as pd
import time
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- PAGE CONFIG ---
st.set_page_config(page_title="Little Linguist Login", page_icon="🔐")

# --- GOOGLE SHEETS SETUP ---
# We use a simplified connection function
def get_google_sheet():
    # We will grab secrets from Streamlit's internal secrets manager
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    # Open the sheet by name
    return client.open("Little Linguist Grades").sheet1

def log_to_sheet(student, word, result, wallet_amt):
    try:
        sheet = get_google_sheet()
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        # Append row: [Date, Time, Student, Word, Result, Wallet]
        sheet.append_row([date_str, time_str, student, word, result, wallet_amt])
    except Exception as e:
        # If logging fails (internet blip), don't crash the app, just print error to console
        print(f"Logging error: {e}")

# --- USER CONFIGURATION ---
USERS = {
    "Nelson": "admin",    
    "Student1": "blue",   
    "Student2": "red",    
}

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'wallet' not in st.session_state: st.session_state.wallet = 0
if 'inventory' not in st.session_state: st.session_state.inventory = []
if 'q_data' not in st.session_state: st.session_state.q_data = None
if 'mistakes' not in st.session_state: st.session_state.mistakes = {}
if 'total_attempts' not in st.session_state: st.session_state.total_attempts = 0
if 'correct_attempts' not in st.session_state: st.session_state.correct_attempts = 0

# --- CURRICULUM ---
curriculum = [
    {"es": "El Dinero", "en": "Money", "emoji": "💵"},
    {"es": "Ahorrar", "en": "To Save", "emoji": "🐖"},
    {"es": "Comprar", "en": "To Buy", "emoji": "🛒"},
    {"es": "La Mamá", "en": "Mom", "emoji": "👩"},
    {"es": "El Papá", "en": "Dad", "emoji": "👨"},
    {"es": "El Gato", "en": "Cat", "emoji": "🐱"},
    {"es": "El Perro", "en": "Dog", "emoji": "🐶"},
    {"es": "La Manzana", "en": "Apple", "emoji": "🍎"},
    {"es": "El Agua", "en": "Water", "emoji": "💧"},
    {"es": "La Pupusa", "en": "Pupusa", "emoji": "🫓"},
    {"es": "La Casa", "en": "House", "emoji": "🏠"},
]

store_items = [
    {"name": "Pupusa", "price": 5, "emoji": "🫓"},
    {"name": "Rocket", "price": 10, "emoji": "🚀"},
    {"name": "Crown", "price": 20, "emoji": "👑"},
    {"name": "Unicorn", "price": 50, "emoji": "🦄"}
]

# --- FUNCTIONS ---
def get_question():
    q = random.choice(curriculum)
    distractors = [x for x in curriculum if x['es'] != q['es']]
    if len(distractors) < 2: opts = [q, q, q]
    else: opts = random.sample(distractors, 2) + [q]
    random.shuffle(opts)
    return {"target": q, "options": opts}

def update_stats(is_correct, word_es):
    st.session_state.total_attempts += 1
    result_str = "Correct"
    if is_correct:
        st.session_state.correct_attempts += 1
    else:
        result_str = "Wrong"
        current_count = st.session_state.mistakes.get(word_es, 0)
        st.session_state.mistakes[word_es] = current_count + 1
    
    # --- LOGGING TO GOOGLE SHEETS ---
    # We do this in the background
    log_to_sheet(st.session_state.user_name, word_es, result_str, st.session_state.wallet)

def login():
    st.title("🔐 Class Login")
    with st.form("login_form"):
        username = st.text_input("Name").strip()
        password = st.text_input("Password", type="password").strip()
        submit = st.form_submit_button("Log In")
        if submit:
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.user_name = username
                st.success(f"Welcome, {username}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Try again")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.rerun()

# --- MAIN LOGIC ---
if not st.session_state.logged_in:
    login()
else:
    with st.sidebar:
        st.write(f"👤 **Student:** {st.session_state.user_name}")
        st.header(f"💰 Wallet: ${st.session_state.wallet}")
        if st.button("Log Out"): logout()
        st.markdown("---")
        with st.expander("🛒 Store", expanded=True):
            for item in store_items:
                if st.button(f"Buy {item['emoji']} (${item['price']})"):
                    if st.session_state.wallet >= item['price']:
                        st.session_state.wallet -= item['price']
                        st.session_state.inventory.append(item['emoji'])
                        st.success("Bought!")
                        # Log purchase
                        log_to_sheet(st.session_state.user_name, f"BOUGHT {item['name']}", "SPEND", st.session_state.wallet)
                    else:
                        st.error("Need more money!")
            st.write(" **Inventory:** " + " ".join(st.session_state.inventory))

    if st.session_state.q_data is None:
        st.session_state.q_data = get_question()
        
    st.title(f"Hola, {st.session_state.user_name}! 🇸🇻")
    st.caption("Listen and choose.")

    target = st.session_state.q_data['target']

    try:
        sound_file = BytesIO()
        tts = gTTS(target['es'], lang='es')
        tts.write_to_fp(sound_file)
        st.audio(sound_file)
    except:
        st.error("Audio busy.")

    cols = st.columns(3)
    for i, opt in enumerate(st.session_state.q_data['options']):
        btn_label = f"{opt['emoji']}\n\n{opt['en']}"
        if cols[i].button(btn_label, use_container_width=True):
            if opt['es'] == target['es']:
                st.session_state.wallet += 1
                update_stats(True, target['es'])
                st.success("¡Correcto!")
                time.sleep(1)
                st.session_state.q_data = get_question()
                st.rerun()
            else:
                update_stats(False, target['es'])
                st.error("Try again!")