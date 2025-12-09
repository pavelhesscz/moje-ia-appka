import streamlit as st
import google.generativeai as genai
import pandas as pd
import json

st.set_page_config(page_title="Pivní Mapa 🍺", page_icon="🍺", layout="wide")

st.title("🍺 Můj AI Pivní Deníček")

# --- 1. PŘIPOJENÍ K AI (Zkopírováno z minula) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("Chybí API klíč!")
    st.stop()

# Funkce pro získání modelu (používáme ten, co minule fungoval)
@st.cache_resource
def get_model():
    # Zkusíme Flash, je rychlý. Když nepůjde, fallback na Pro.
    try:
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return genai.GenerativeModel('gemini-pro')

model = get_model()

# --- 2. PAMĚŤ APLIKACE (Session State) ---
# Tady ukládáme piva, dokud je aplikace otevřená
if 'piva' not in st.session_state:
    st.session_state.piva = []

# --- 3. FORMULÁŘ PRO PŘIDÁNÍ PIVA ---
with st.sidebar:
    st.header("🍻 Přidat nový kousek")
    nazev_piva = st.text_input("Jméno piva", placeholder="např. Guinness")
    misto = st.text_input("Kde jsi ho pil/a?", placeholder="např. Dublin, Temple Bar")
    hodnoceni = st.slider("Hodnocení (1-5)", 1, 5, 5)
    
    btn_pridat = st.button("Zaznamenat a najít na mapě")

# --- 4. LOGIKA PŘIDÁNÍ (Tady kouzlí AI) ---
if btn_pridat and nazev_piva and misto:
    with st.spinner('AI hledá informace o pivu a GPS souřadnice...'):
        try:
            # Zeptáme se AI, ať nám vrátí strukturovaná data (JSON)
            prompt = f"""
            Mám pivo '{nazev_piva}' vypité v místě '{misto}'.
            Vrať mi pouze čistý JSON (bez markdownu) s těmito klíči:
            "styl": (odhadni styl piva, např. Ležák, Stout),
            "alkohol": (odhadni % alkoholu jako číslo, např. 4.2),
            "popis": (krátká zajímavost o pivu jednou větou česky),
            "lat": (zeměpisná šířka místa '{misto}' jako číslo),
            "lon": (zeměpisná délka místa '{misto}' jako číslo)
            """
            
            response = model.generate_content(prompt)
            text_response = response.text.strip()
            
            # Očištění odpovědi, kdyby tam AI nechala "```json"
            if text_response.startswith("```"):
                text_response = text_response.replace("```json", "").replace("```", "")
            
            data = json.loads(text_response)
            
            # Přidání do našeho seznamu
            novy_zaznam = {
                "Pivo": nazev_piva,
                "Místo": misto,
                "Styl": data.get("styl", "Neznámý"),
                "Alkohol": f"{data.get('alkohol', '?')}%",
                "Popis": data.get("popis", ""),
                "Hodnocení": "⭐" * hodnoceni,
                "lat": data.get("lat"),
                "lon": data.get("lon")
            }
            
            st.session_state.piva.append(novy_zaznam)
            st.success(f"Přidáno: {nazev_piva}!")
            
        except Exception as e:
            st.error(f"Nepodařilo se načíst data. Zkus to znovu. Chyba: {e}")

# --- 5. ZOBRAZENÍ MAPY A TABULKY ---

col1, col2 = st.columns([2, 1])

if st.session_state.piva:
    df = pd.DataFrame(st.session_state.piva)
    
    with col1:
        st.subheader("🌍 Mapa ochutnávek")
        # Streamlit mapa potřebuje sloupce 'lat' a 'lon'
        if 'lat' in df.columns and 'lon' in df.columns:
            # Vyfiltrujeme záznamy, kde se GPS nepovedlo
            map_data = df.dropna(subset=['lat', 'lon'])
            st.map(map_data, zoom=4)
        else:
            st.warning("Zatím nemám žádná data pro mapu.")

    with col2:
        st.subheader("📝 Seznam")
        # Ukážeme zjednodušenou tabulku bez GPS
        display_df = df[["Pivo", "Styl", "Místo", "Hodnocení", "Popis"]]
        st.dataframe(display_df, hide_index=True)
else:
    st.info("Zatím jsi nic nevypil/a. Přidej první pivo v menu vlevo! 👈")

# Tlačítko pro smazání seznamu
if st.sidebar.button("🗑️ Vymazat seznam"):
    st.session_state.piva = []
    st.rerun()
