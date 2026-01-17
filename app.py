# To run this, you would need a file named app.py
import streamlit as st
import random
from gtts import gTTS
from io import BytesIO
import pandas as pd
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Little Linguist Login", page_icon="🔐")

# --- USER CONFIGURATION (EDIT THIS!) ---
# Format: "Username": "Password"
USERS = {
    "Nelson": "admin",    # You (Teacher)
    "Santi": "blue",   # Kid 1 (Password is simple color)
    "Ceci": "red",    # Kid 2
}

# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'wallet' not in st.session_state: st.session_state.wallet = 0
if 'inventory' not in st.session_state: st.session_state.inventory = []
if 'q_data' not in st.session_state: st.session_state.q_data = None
if 'mistakes' not in st.session_state: st.session_state.mistakes = {}
if 'total_attempts' not in st.session_state: st.session_state.total_attempts = 0
if 'correct_attempts' not in st.session_state: st.session_state.correct_attempts = 0

# --- DATA: CURRICULUM ---
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
    # Ensure distinct distractors
    if len(distractors) < 2:
        opts = [q, q, q] # Fallback
    else:
        opts = random.sample(distractors, 2) + [q]
    random.shuffle(opts)
    return {"target": q, "options": opts}

def update_stats(is_correct, word_es):
    st.session_state.total_attempts += 1
    if is_correct:
        st.session_state.correct_attempts += 1
    else:
        current_count = st.session_state.mistakes.get(word_es, 0)
        st.session_state.mistakes[word_es] = current_count + 1

def login():
    st.title("🔐 Class Login")
    st.write("Please sign in to start learning.")
    
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
                st.error("Incorrect name or password")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    # Optional: Clear stats on logout? 
    # st.session_state.wallet = 0 
    st.rerun()

# --- MAIN APP LOGIC ---

if not st.session_state.logged_in:
    login()
else:
    # === THE GAME STARTS HERE ===
    
    # Sidebar
    with st.sidebar:
        st.write(f"👤 **Student:** {st.session_state.user_name}")
        st.header(f"💰 Wallet: ${st.session_state.wallet}")
        
        if st.button("Log Out"):
            logout()
            
        st.markdown("---")
        
        # Store
        with st.expander("🛒 La Tienda", expanded=True):
            for item in store_items:
                if st.button(f"Buy {item['emoji']} (${item['price']})"):
                    if st.session_state.wallet >= item['price']:
                        st.session_state.wallet -= item['price']
                        st.session_state.inventory.append(item['emoji'])
                        st.success("Bought!")
                    else:
                        st.error("Not enough money!")
            st.write(" **Inventory:** " + " ".join(st.session_state.inventory))

        # Stats
        with st.expander("📊 Report Card", expanded=False):
            st.write(f"Stats for: {st.session_state.user_name}")
            if st.session_state.total_attempts > 0:
                acc = (st.session_state.correct_attempts / st.session_state.total_attempts) * 100
                st.metric("Accuracy", f"{acc:.0f}%")
                if st.session_state.mistakes:
                    df = pd.DataFrame(list(st.session_state.mistakes.items()), columns=['Word', 'Mistakes'])
                    st.dataframe(df, hide_index=True)
            else:
                st.write("Play to see stats.")

    # Main Area
    if st.session_state.q_data is None:
        st.session_state.q_data = get_question()
        
    st.title(f"Hola, {st.session_state.user_name}! 🇸🇻")
    st.caption("Listen and choose.")

    target = st.session_state.q_data['target']

    # Audio
    try:
        sound_file = BytesIO()
        tts = gTTS(target['es'], lang='es')
        tts.write_to_fp(sound_file)
        st.audio(sound_file)
    except:
        st.error("Audio busy. Click button below to skip.")

    st.write("") 

    # Buttons
    cols = st.columns(3)
    for i, opt in enumerate(st.session_state.q_data['options']):
        btn_label = f"{opt['emoji']}\n\n{opt['en']}"
        
        if cols[i].button(btn_label, use_container_width=True):
            if opt['es'] == target['es']:
                st.session_state.wallet += 1
                update_stats(True, target['es'])
                st.success("¡Correcto!")
                time.sleep(1) # Pause to see the green success message
                st.session_state.q_data = get_question()
                st.rerun()
            else:
                update_stats(False, target['es'])
                st.error("Try again!")