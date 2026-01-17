# To run this, you would need a file named app.py
import streamlit as st
import random
from gtts import gTTS
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Spanish & Finance", page_icon="🏦")

# --- SESSION STATE (Memory) ---
if 'wallet' not in st.session_state: st.session_state.wallet = 0
if 'inventory' not in st.session_state: st.session_state.inventory = []
if 'q_data' not in st.session_state: st.session_state.q_data = None

# --- DATA ---
curriculum = [
    {"es": "El Dinero", "en": "Money", "emoji": "💵"},
    {"es": "Ahorrar", "en": "To Save", "emoji": "🐖"},
    {"es": "El Gato", "en": "The Cat", "emoji": "🐱"}
]

store_items = [
    {"name": "Cookie", "price": 5, "emoji": "🍪"},
    {"name": "Rocket", "price": 10, "emoji": "🚀"}
]

# --- FUNCTIONS ---
def get_question():
    q = random.choice(curriculum)
    distractors = [x['en'] for x in curriculum if x['en'] != q['en']]
    if len(distractors) < 2: distractors += ["Dog", "Blue"]
    opts = random.sample(distractors, 2) + [q['en']]
    random.shuffle(opts)
    return {"q": q, "opts": opts}

if st.session_state.q_data is None:
    st.session_state.q_data = get_question()

# --- SIDEBAR (The Store) ---
with st.sidebar:
    st.header(f"💰 Wallet: ${st.session_state.wallet}")
    st.write("### La Tienda (Store)")
    for item in store_items:
        if st.button(f"Buy {item['emoji']} (${item['price']})"):
            if st.session_state.wallet >= item['price']:
                st.session_state.wallet -= item['price']
                st.session_state.inventory.append(item['emoji'])
                st.success("Bought!")
            else:
                st.error("Not enough money!")
    
    st.write("### My Inventory:")
    st.write(" ".join(st.session_state.inventory))

# --- MAIN PAGE (The Game) ---
st.title("Little Linguist 🇪🇸")

q = st.session_state.q_data['q']

st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{q['emoji']}</h1>", unsafe_allow_html=True)
st.markdown(f"<h2 style='text-align: center;'>{q['es']}</h2>", unsafe_allow_html=True)

# Audio Generation (Cached)
tts = gTTS(q['es'], lang='es')
tts.save('audio.mp3')
st.audio('audio.mp3')

# Answer Buttons
cols = st.columns(3)
for i, opt in enumerate(st.session_state.q_data['opts']):
    if cols[i].button(opt, use_container_width=True):
        if opt == q['en']:
            st.session_state.wallet += 1
            st.success("Correct! +$1")
            st.session_state.q_data = get_question() # New Question
            st.rerun()
        else:
            st.error("Try again!")