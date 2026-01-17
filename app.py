# To run this, you would need a file named app.py
import streamlit as st
import random
from gtts import gTTS
from io import BytesIO

# --- PAGE CONFIG ---
st.set_page_config(page_title="Spanish for Kids", page_icon="🇸🇻")

# --- SESSION STATE ---
if 'wallet' not in st.session_state: st.session_state.wallet = 0
if 'inventory' not in st.session_state: st.session_state.inventory = []
if 'q_data' not in st.session_state: st.session_state.q_data = None

# --- DATA: EXTENDED CURRICULUM (25+ Words) ---
curriculum = [
    # Finance Module (Keep these!)
    {"es": "El Dinero", "en": "Money", "emoji": "💵"},
    {"es": "Ahorrar", "en": "To Save", "emoji": "🐖"},
    {"es": "Comprar", "en": "To Buy", "emoji": "🛒"},
    
    # Original Animals
    {"es": "El Gato", "en": "The Cat", "emoji": "🐱"},
    {"es": "El Perro", "en": "The Dog", "emoji": "🐶"},
    
    # NEW: Family (La Familia)
    {"es": "La Mamá", "en": "Mom", "emoji": "👩"},
    {"es": "El Papá", "en": "Dad", "emoji": "👨"},
    {"es": "El Bebé", "en": "Baby", "emoji": "👶"},
    {"es": "La Abuela", "en": "Grandma", "emoji": "👵"},
    {"es": "El Abuelo", "en": "Grandpa", "emoji": "👴"},
    
    # NEW: Food (La Comida)
    {"es": "La Manzana", "en": "Apple", "emoji": "🍎"},
    {"es": "El Plátano", "en": "Banana", "emoji": "🍌"},
    {"es": "El Agua", "en": "Water", "emoji": "💧"},
    {"es": "La Leche", "en": "Milk", "emoji": "🥛"},
    {"es": "El Pan", "en": "Bread", "emoji": "🍞"},
    {"es": "El Huevo", "en": "Egg", "emoji": "🥚"},
    
    # NEW: Nature & Home
    {"es": "El Sol", "en": "Sun", "emoji": "☀️"},
    {"es": "La Luna", "en": "Moon", "emoji": "🌙"},
    {"es": "La Estrella", "en": "Star", "emoji": "⭐"},
    {"es": "La Casa", "en": "House", "emoji": "🏠"},
    {"es": "El Libro", "en": "Book", "emoji": "📚"},
    {"es": "La Flor", "en": "Flower", "emoji": "🌸"},
    
    # NEW: More Animals
    {"es": "El León", "en": "Lion", "emoji": "🦁"},
    {"es": "El Elefante", "en": "Elephant", "emoji": "🐘"},
    {"es": "La Mariposa", "en": "Butterfly", "emoji": "🦋"},
    
    # NEW: Body
    {"es": "La Mano", "en": "Hand", "emoji": "✋"},
    {"es": "El Pie", "en": "Foot", "emoji": "🦶"}
]

store_items = [
    {"name": "Pupusa", "price": 5, "emoji": "🫓"}, # Updated to Pupusa for El Salvador!
    {"name": "Rocket", "price": 10, "emoji": "🚀"},
    {"name": "Crown", "price": 20, "emoji": "👑"},
    {"name": "Unicorn", "price": 50, "emoji": "🦄"}
]

# --- FUNCTIONS ---
def get_question():
    q = random.choice(curriculum)
    distractors = [x['en'] for x in curriculum if x['en'] != q['en']]
    # Fallback if somehow not enough distractors
    while len(distractors) < 2:
        distractors.append("Apple")
        distractors.append("Run")
        
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
        if st.button(f"Buy {item['emoji']} {item['name']} (${item['price']})"):
            if st.session_state.wallet >= item['price']:
                st.session_state.wallet -= item['price']
                st.session_state.inventory.append(item['emoji'])
                st.success(f"Bought {item['name']}!")
            else:
                st.error("Not enough money!")
    
    st.write("### My Inventory:")
    # Display inventory as a grid of emojis
    st.write(" ".join(st.session_state.inventory))

# --- MAIN PAGE (The Game) ---
st.title("Little Linguist El Salvador 🇸🇻") 

q = st.session_state.q_data['q']

# Display Emoji and Text
st.markdown(f"<h1 style='text-align: center; font-size: 100px;'>{q['emoji']}</h1>", unsafe_allow_html=True)
st.markdown(f"<h2 style='text-align: center;'>{q['es']}</h2>", unsafe_allow_html=True)

# Cloud Safe Audio
try:
    sound_file = BytesIO()
    tts = gTTS(q['es'], lang='es')
    tts.write_to_fp(sound_file)
    st.audio(sound_file)
except Exception as e:
    st.error("Audio error (Cloud busy). Try next word!")

# Answer Buttons
cols = st.columns(3)
for i, opt in enumerate(st.session_state.q_data['opts']):
    if cols[i].button(opt, use_container_width=True):
        if opt == q['en']:
            st.session_state.wallet += 1
            st.success("Correct! +$1")
            st.session_state.q_data = get_question()
            st.rerun()
        else:
            st.error("Try again!")