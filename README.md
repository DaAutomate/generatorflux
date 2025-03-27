# Generator Obrazów FLUX1.1 Pro

Aplikacja Streamlit do generowania obrazów przy użyciu modelu FLUX1.1 Pro. Aplikacja pozwala na tworzenie wysokiej jakości obrazów na podstawie opisów tekstowych.

## Funkcje

- Generowanie obrazów na podstawie opisów tekstowych
- Konfiguracja parametrów generowania (format, proporcje, poziom bezpieczeństwa)
- Możliwość pobrania wygenerowanych obrazów
- Wskazówki dotyczące tworzenia efektywnych opisów

## Wymagania

- Python 3.8+
- Streamlit
- fal-client
- Pillow
- Requests

## Instalacja

```bash
pip install -r requirements.txt
```

## Uruchomienie

```bash
streamlit run app.py
```

## Konfiguracja

Aby używać aplikacji, potrzebujesz klucza API FLUX. Klucz API składa się z dwóch części:
- ID klucza API
- Sekret klucza API

Wprowadź obie części klucza w panelu bocznym aplikacji.

## Przykładowy opis obrazu

```
Fotorealistyczne śniadanie dla diety przeciwzapalnej: miska owsianki z nasionami chia, 
świeżymi borówkami, płatkami migdałów i odrobiną miodu. Łyżka obok miski, czysty stół, 
przytulne poranne oświetlenie, bez etykiet czy tekstu, wysokiej rozdzielczości fotografia kulinarna.
```