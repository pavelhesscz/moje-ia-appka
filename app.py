import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Moje AI Apka", page_icon="🤖")
st.title("🤖 Moje AI Aplikace")

# 1. Konfigurace API klíče
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("Chybí API klíč! Nastav ho v Secrets na Streamlit Cloudu.")
    st.stop()

# 2. Získání seznamu funkčních modelů
@st.cache_resource
def get_available_models():
    try:
        model_list = []
        # Projdeme vše, co Google nabízí
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Vyčistíme název (odstraníme 'models/')
                clean_name = m.name.replace("models/", "")
                model_list.append(clean_name)
        return sorted(model_list, reverse=True) # Seřadíme, nejnovější nahoře
    except Exception as e:
        st.error(f"Chyba při načítání modelů: {e}")
        return []

# Načteme modely do seznamu
dostupne_modely = get_available_models()

if not dostupne_modely:
    st.error("❌ Tvůj API klíč nevidí žádné modely. Zkus vygenerovat nový klíč v AI Studiu.")
    st.stop()

# 3. VÝBĚR MODELU (Rozbalovací menu)
st.write("### Nastavení")
vybrany_model = st.selectbox(
    "Vyber si model (když jeden nejde, zkus jiný):", 
    dostupne_modely,
    index=0 # Vybere automaticky ten první v seznamu
)

# 4. Samotná aplikace
st.divider() # Čára pro oddělení
st.write(f"Svištíme na modelu: **{vybrany_model}**")

user_input = st.text_area("Na co se chceš zeptat?", height=150)

if st.button("Odeslat dotaz"):
    if user_input:
        with st.spinner('AI přemýšlí...'):
            try:
                # Tady použijeme přesně to, co sis vybral v menu
                model = genai.GenerativeModel(vybrany_model)
                response = model.generate_content(user_input)
                
                st.write("### Odpověď:")
                st.write(response.text)
                
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg:
                    st.error("🛑 DOŠEL LIMIT (Error 429).")
                    st.warning("Tento model jsi dnes už vyčerpal. ⬆️ Vyber v menu nahoře jiný model (třeba nějaký s 'flash').")
                elif "404" in err_msg:
                    st.error("🛑 Model nenalezen (Error 404).")
                    st.warning("Google tento model v tvém regionu nepodporuje. ⬆️ Zkus vybrat jiný.")
                else:
                    st.error(f"Neočekávaná chyba: {e}")
    else:
        st.warning("Napřed musíš něco napsat.")
