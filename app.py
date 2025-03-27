import streamlit as st
import os
import time
import requests
from PIL import Image
from io import BytesIO
import fal_client

st.set_page_config(
    page_title="Generator Obrazów FLUX",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Generator Obrazów FLUX1.1 Pro")
st.write("Generuj niesamowite obrazy przy użyciu modelu FLUX1.1 Pro")

# Sprawdź, czy sekrety są skonfigurowane
if 'FAL_KEY_ID' in st.secrets and 'FAL_KEY_SECRET' in st.secrets:
    # Odczytaj klucze API z sekretów
    fal_key_id = st.secrets["FAL_KEY_ID"]
    fal_key_secret = st.secrets["FAL_KEY_SECRET"]
    keys_from_secrets = True
else:
    # Jeśli sekrety nie są dostępne, pozwól na ręczne wprowadzenie
    fal_key_id = None
    fal_key_secret = None
    keys_from_secrets = False

# Panel boczny dla opcji
with st.sidebar:
    st.header("Konfiguracja")
    
    # Pole wprowadzania klucza API tylko jeśli nie znaleziono w sekretach
    if not keys_from_secrets:
        st.warning("Klucze API nie są skonfigurowane w sekretach. Wprowadź je ręcznie:")
        fal_key_id = st.text_input("Wprowadź ID klucza API", type="password", help="Pierwsza część klucza API")
        fal_key_secret = st.text_input("Wprowadź sekret klucza API", type="password", help="Druga część klucza API")
    else:
        st.success("Klucze API zostały wczytane z sekretów Streamlit")
    
    st.markdown("---")
    
    # Opcje modelu
    st.subheader("Ustawienia Modelu")
    
    # Opcje bezpieczeństwa
    enable_safety = st.checkbox("Włącz filtr bezpieczeństwa", value=True)
    
    safety_options = {
        "1": "Bardzo Restrykcyjny",
        "2": "Restrykcyjny (Domyślny)",
        "3": "Umiarkowany",
        "4": "Liberalny",
        "5": "Bardzo Liberalny",
        "6": "Bez ograniczeń"
    }
    
    safety_tolerance = st.select_slider(
        "Poziom bezpieczeństwa",
        options=list(safety_options.keys()),
        value="2",
        format_func=lambda x: safety_options[x]
    )
    
    # Format wyjściowy
    output_format = st.radio("Format obrazu", ["jpeg", "png"], index=0)
    
    # Proporcje obrazu
    aspect_ratios = {
        "21:9": "Ultra szeroki (21:9)",
        "16:9": "Panoramiczny (16:9)",
        "4:3": "Standardowy (4:3)",
        "3:2": "Foto (3:2)",
        "1:1": "Kwadratowy (1:1)",
        "2:3": "Portretowy foto (2:3)",
        "3:4": "Portretowy standardowy (3:4)",
        "9:16": "Portretowy panoramiczny (9:16)",
        "9:21": "Portretowy ultra szeroki (9:21)"
    }
    
    aspect_ratio = st.selectbox(
        "Proporcje obrazu",
        options=list(aspect_ratios.keys()),
        index=1,  # 16:9 domyślnie
        format_func=lambda x: aspect_ratios[x]
    )
    
    # Tryb surowy - domyślnie wyłączony zgodnie z dokumentacją
    raw_mode = st.checkbox("Tryb surowy (mniej przetworzony, bardziej naturalny)", value=False)
    
    # Ustawienia zaawansowane
    st.markdown("---")
    st.subheader("Ustawienia Zaawansowane")
    
    # Ziarno dla powtarzalności
    use_seed = st.checkbox("Użyj określonego ziarna", value=False)
    seed = None
    if use_seed:
        seed = st.number_input("Wartość ziarna", min_value=0, max_value=2147483647, value=42)

# Główna część
prompt = st.text_area(
    "Wprowadź opis obrazu:",
    height=100,
    placeholder="Opisz szczegółowo obraz, który chcesz wygenerować...",
    help="Im bardziej szczegółowy opis, tym lepsze rezultaty"
)

# Wskaźniki statusu
status_placeholder = st.empty()
progress_bar = st.empty()
image_placeholder = st.empty()
result_info = st.empty()

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            status_placeholder.info(log["message"])

def generate_image():
    if not fal_key_id or not fal_key_secret:
        st.error("⚠️ Klucze API nie są dostępne. Skonfiguruj sekrety lub wprowadź klucze ręcznie.")
        return
    
    if not prompt:
        st.error("⚠️ Proszę wprowadzić opis obrazu")
        return
    
    # Ustawienie klucza API
    fal_client.api_key = f"{fal_key_id}:{fal_key_secret}"
    
    # Przygotuj argumenty - używając dokładnie tych samych nazw parametrów i domyślnych wartości jak w dokumentacji
    arguments = {
        "prompt": prompt,
        "num_images": 1,  # zawsze generuj 1 obraz
        "enable_safety_checker": enable_safety,
        "safety_tolerance": safety_tolerance,
        "output_format": output_format,
        "aspect_ratio": aspect_ratio,
        "raw": raw_mode  # zawsze dodajemy parametr raw (true lub false)
    }
        
    # Dodaj ziarno tylko jeśli jest określone
    if use_seed and seed is not None:
        arguments["seed"] = seed
    
    status_placeholder.info("Rozpoczynam generowanie obrazu...")
    progress_bar.progress(0)
    
    try:
        start_time = time.time()
        
        # Wywołanie API zgodnie z dokumentacją
        result = fal_client.subscribe(
            "fal-ai/flux-pro/v1.1-ultra",
            arguments,
            with_logs=True,
            on_queue_update=on_queue_update
        )
        
        end_time = time.time()
        progress_bar.progress(100)
        status_placeholder.success("✅ Obraz wygenerowany pomyślnie!")
        
        # Wyświetl wygenerowany obraz
        if result and "images" in result and len(result["images"]) > 0:
            image_url = result["images"][0]["url"]
            
            # Pobierz i wyświetl obraz
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            image_placeholder.image(img, caption="Wygenerowany obraz", use_column_width=True)
            
            # Pokaż informacje o rezultacie
            result_info.json({
                "Czas generowania": f"{end_time - start_time:.2f} sekund",
                "Opis": result.get("prompt", prompt),
                "Ziarno": result.get("seed", "Losowe"),
                "Proporcje": aspect_ratio
            })
            
            # Przycisk do pobrania
            img_data = BytesIO()
            img.save(img_data, format=output_format.upper())
            st.download_button(
                label="Pobierz obraz",
                data=img_data.getvalue(),
                file_name=f"flux_obraz_{int(time.time())}.{output_format}",
                mime=f"image/{output_format}"
            )
        else:
            st.error("Nie zwrócono żadnego obrazu w wyniku")
            st.write(result)
            
    except Exception as e:
        progress_bar.empty()
        status_placeholder.error(f"Błąd podczas generowania obrazu: {str(e)}")
        st.exception(e)

# Przycisk generowania
if st.button("🔮 Generuj Obraz", type="primary", use_container_width=True):
    generate_image()

# Dodaj wskazówki
with st.expander("Wskazówki do tworzenia lepszych opisów"):
    st.markdown("""
    ### Wskazówki do tworzenia efektywnych opisów:
    
    1. **Bądź konkretny i szczegółowy** - Opisz dokładnie to, czego oczekujesz, włączając temat, styl, oświetlenie, perspektywę, itp.
    2. **Wspomnij o stylach artystycznych** - Odwołania do konkretnych stylów jak "obraz olejny", "akwarela", "sztuka cyfrowa", "fotorealistyczny", itp.
    3. **Nawiązuj do artystów** - Wspomnienie artystów może pomóc w ukierunkowaniu stylu (np. "w stylu Moneta")
    4. **Opisz oświetlenie** - Terminy jak "złota godzina", "dramatyczne cienie", "miękkie światło otoczenia"
    5. **Określ szczegóły aparatu** - Uwzględnij terminy jak "szeroki kąt", "portret", "zbliżenie", "widok z lotu ptaka"
    
    ### Przykładowy poprawny opis:
    ```
    Fotorealistyczne śniadanie dla diety przeciwzapalnej: miska owsianki z nasionami chia, świeżymi borówkami, płatkami migdałów i odrobiną miodu. Łyżka obok miski, czysty stół, przytulne poranne oświetlenie, bez etykiet czy tekstu, wysokiej rozdzielczości fotografia kulinarna.
    ```
    """)

# Instrukcja konfiguracji sekretów
with st.expander("Jak skonfigurować sekrety API w Streamlit"):
    st.markdown("""
    ### Konfiguracja sekretów API w Streamlit Community Cloud

    1. Otwórz swoją aplikację w Streamlit Community Cloud
    2. Kliknij przycisk z trzema kropkami (⋮) w prawym górnym rogu
    3. Wybierz "Settings"
    4. Przewiń w dół do sekcji "Secrets"
    5. Kliknij "Edit secrets"
    6. Wklej swoje sekrety w formacie TOML:

    ```toml
    FAL_KEY_ID = "twój-id-klucza"
    FAL_KEY_SECRET = "twój-sekret-klucza"
    ```

    7. Kliknij "Save"
    8. Uruchom ponownie aplikację
    """)

# Stopka
st.markdown("---")
st.caption("Generator Obrazów FLUX1.1 Pro - Wszystkie obrazy są generowane przy użyciu FLUX1.1 Pro. Używaj odpowiedzialnie i przestrzegaj Warunków Korzystania z FLUX1.1 PRO.")