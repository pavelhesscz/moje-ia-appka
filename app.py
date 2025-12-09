import streamlit as st
import google.generativeai as genai

st.title("🤖 Moje AI Aplikace")

# 1. Načtení klíče
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("Chybí API klíč! Nastav ho v Secrets.")
    st.stop()

# 2. Nastavení modelu "natvrdo" na stabilní verzi zdarma
# Pokud 1.5-flash nebude fungovat, zkusíme 'gemini-pro'
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Rychlý test, jestli model žije (ping)
    response = model.generate_content("test", request_options={"timeout": 5})
except:
    # Záložní plán - starší model, pokud Flash stávkuje
    st.warning("Přepínám na záložní model Gemini Pro...")
    model = genai.GenerativeModel('gemini-pro')

st.success("✅ Připojeno k modelu.")

# 3. Rozhraní aplikace
user_input = st.text_area("Na co se chceš zeptat?", height=150)

if st.button("Odeslat dotaz"):
    if user_input:
        with st.spinner('AI přemýšlí...'):
            try:
                response = model.generate_content(user_input)
                st.write("### Odpověď:")
                st.write(response.text)
            except Exception as e:
                # Pokud dojde k chybě 429 i tady, vypíšeme česky co dělat
                if "429" in str(e):
                    st.error("🛑 DOŠEL LIMIT ZDARMA (Error 429).")
                    st.info("Řešení: V Google AI Studiu si vytvoř úplně nový Google účet a nový klíč, vyčerpal jsi denní příděl.")
                else:
                    st.error(f"Chyba: {e}")
    else:
        st.warning("Napřed musíš něco napsat.")
