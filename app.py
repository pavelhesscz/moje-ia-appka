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

# 2. AUTOMATICKÉ HLEDÁNÍ MODELU (To opraví tvou chybu)
@st.cache_resource
def get_working_model():
    try:
        # Zeptáme se Googlu: "Co mám k dispozici?"
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Vrátíme první model, který umí psát text (bez "models/" na začátku)
                return m.name
    except Exception as e:
        return None

# Zjistíme název modelu
model_name = get_working_model()

if model_name:
    # Pokud je v názvu 'models/', odstraníme to pro jistotu
    if model_name.startswith("models/"):
        final_name = model_name.split("/")[-1]
    else:
        final_name = model_name
        
    st.success(f"✅ Automaticky připojeno k modelu: **{final_name}**")
    model = genai.GenerativeModel(final_name)

    # 3. Samotná aplikace
    user_input = st.text_area("Na co se chceš zeptat?", height=150)

    if st.button("Odeslat dotaz"):
        if user_input:
            with st.spinner('AI přemýšlí...'):
                try:
                    response = model.generate_content(user_input)
                    st.write("### Odpověď:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Chyba při generování: {e}")
        else:
            st.warning("Napřed musíš něco napsat.")

else:
    # Pokud script nenašel ŽÁDNÝ model
    st.error("❌ Kritická chyba: Tvůj API klíč nevidí žádné modely.")
    st.info("Tip: Jdi do AI Studia a vygeneruj si úplně nový klíč.")
    # Pro jistotu vypíšeme detail chyby, pokud to půjde
    try:
        list(genai.list_models())
    except Exception as e:
        st.code(f"Detail chyby od Googlu: {e}")
