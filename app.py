import streamlit as st
import google.generativeai as genai

# Nadpis aplikace
st.title("🤖 Moje AI Aplikace")

# Konfigurace klíče (bere ho z tajného uložiště Streamlitu)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("Chybí API klíč! Nastav ho v Secrets na Streamlit Cloudu.")

# Výběr modelu (zde používáme flash, je rychlý a zdarma)
model = genai.GenerativeModel('gemini-pro')

# Textové pole pro uživatele
user_input = st.text_area("Na co se chceš zeptat?", height=150)

# Tlačítko
if st.button("Odeslat dotaz"):
    if user_input:
        with st.spinner('AI přemýšlí...'):
            try:
                response = model.generate_content(user_input)
                st.write("### Odpověď:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Chyba: {e}")
    else:
        st.warning("Napřed musíš něco napsat.")
