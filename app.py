# To run this, you would need a file named app.py
import streamlit as st
import random
from gtts import gTTS
from io import BytesIO
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Listen & Learn 🇸🇻", page_icon="👂")

# --- SESSION STATE ---
if 'wallet' not in st.session_state: st.session_state.wallet = 0
if 'inventory' not in st.session_state: st.session_state.inventory = []
if 'q_data' not in st.session_state: st.session_state.q_data = None

# New: Tracking Stats for Parent Dashboard
if 'total_attempts' not in st.session_state: st.session_state.total_attempts = 0
if 'correct_attempts' not in st.session_state: st.session_state.correct_attempts = 0
if 'mistakes' not in st.session_state: st.session_state.mistakes = {} # format: {'El Gato': 2}

# --- DATA: CURRICULUM ---
curriculum = [
    # Finance
    {"es": "El Dinero", "en": "Money", "emoji": "💵"},
    {"es": "Ahorrar", "en": "To Save", "emoji": "🐖"},
    {"es": "Comprar", "en": "To Buy", "emoji": "🛒"},
    # Family
    {"es": "La Mamá", "en": "Mom", "emoji": "👩"},
    {"es": "El Papá", "en": "Dad", "emoji": "👨"},
    {"es": "El Bebé", "en": "Baby", "emoji": "👶"},
    {"es": "La Abuela", "en": "Grandma", "emoji": "👵"},
    {"es": "El Abuelo", "en": "Grandpa", "emoji": "👴"},
    # Food
    {"es": "La Manzana", "en": "Apple", "emoji": "🍎"},
    {"es": "El Plátano", "en": "Banana", "emoji": "🍌"},
    {"es": "El Agua", "en": "Water", "emoji": "💧"},
    {"es": "La Leche", "en": "Milk", "emoji": "🥛"},
    {"es": "El Pan", "en": "Bread", "emoji": "🍞"},
    {"es": "La Pupusa", "en": "Pupusa", "emoji": "🫓"},
    # Nature/Home
    {"es": "El Sol", "en": "Sun", "emoji": "☀️"},
    {"es": "La Luna", "en": "Moon", "emoji": "🌙"},
    {"es": "La Casa", "en": "House", "emoji": "🏠"},
    {"es": "El Libro", "en": "Book", "emoji": "📚"},
    # Animals
    {"es": "El Gato", "en": "Cat", "emoji": "🐱"},
    {"es": "El Perro", "en": "Dog", "emoji": "🐶"},
    {"es": "El León", "en": "Lion", "emoji": "🦁"},
    {"es": "El Elefante", "en": "Elephant", "emoji": "🐘"},
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
    # Get distractors (Whole objects, not just text)
    distractors = [x for x in curriculum if x['es'] != q['es']]
    
    # Pick 2 random distractors
    opts = random.sample(distractors, 2) + [q]
    random.shuffle(opts)
    return {"target": q, "options": opts}

def update_stats(is_correct, word_es):
    st.session_state.total_attempts += 1
    if is_correct:
        st.session_state.correct_attempts += 1
    else:
        # Log the mistake
        current_count = st.session_state.mistakes.get(word_es, 0)
        st.session_state.mistakes[word_es] = current_count + 1

if st.session_state.q_data is None:
    st.session_state.q_data = get_question()

# --- SIDEBAR: STORE & DASHBOARD ---
with st.sidebar:
    st.header(f"💰 Wallet: ${st.session_state.wallet}")
    
    # 1. The Store
    with st.expander("🛒 La Tienda (Store)", expanded=True):
        for item in store_items:
            if st.button(f"Buy {item['emoji']} (${item['price']})"):
                if st.session_state.wallet >= item['price']:
                    st.session_state.wallet -= item['price']
                    st.session_state.inventory.append(item['emoji'])
                    st.success("Bought!")
                else:
                    st.error("Need more money!")
        st.write(" **My Inventory:** " + " ".join(st.session_state.inventory))

    st.markdown("---")

    # 2. Parent Dashboard (Nelson's View)
    with st.expander("📊 Parent Dashboard (Teacher Mode)", expanded=False):
        if st.session_state.total_attempts > 0:
            acc = (st.session_state.correct_attempts / st.session_state.total_attempts) * 100
            st.metric("Accuracy", f"{acc:.0f}%", f"{st.session_state.total_attempts} tries")
            
            if st.session_state.mistakes:
                st.write("**⚠️ Needs Practice:**")
                # Convert dict to DataFrame for nice display
                df = pd.DataFrame(list(st.session_state.mistakes.items()), columns=['Word', 'Errors'])
                st.dataframe(df, hide_index=True)
            else:
                st.write("No mistakes yet! 🎉")
        else:
            st.write("Waiting for data...")

# --- MAIN GAME AREA ---
st.title("Listen & Choose 👂")
st.caption("Click Play, Listen, then choose the picture!")

target = st.session_state.q_data['target']

# 1. AUDIO PLAYER (Center Stage)
# We hide the text/emoji. Only Audio.
try:
    sound_file = BytesIO()
    tts = gTTS(target['es'], lang='es')
    tts.write_to_fp(sound_file)
    st.audio(sound_file)
except:
    st.error("Audio service busy. Click 'Next' to skip.")

st.write("") # Spacer

# 2. ANSWER BUTTONS (The Visuals)
cols = st.columns(3)
for i, opt in enumerate(st.session_state.q_data['options']):
    # Button Label is Emoji + English
    btn_label = f"{opt['emoji']}\n\n{opt['en']}"
    
    if cols[i].button(btn_label, use_container_width=True, help="Click to answer"):
        if opt['es'] == target['es']:
            # CORRECT
            st.session_state.wallet += 1
            update_stats(True, target['es'])
            st.success(f"¡Sí! That was **{target['es']}**!")
            st.session_state.q_data = get_question()
            st.rerun()
        else:
            # WRONG
            update_stats(False, target['es'])
            st.error("Not that one... Listen again!")