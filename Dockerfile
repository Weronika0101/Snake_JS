# Pobierz oficjalny obraz Pythona jako podstawę
FROM python:3.8

# Utwórz i ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj plik requirements.txt do katalogu roboczego
COPY requirements.txt .

# Zainstaluj zależności wymienione w pliku requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj cały kod projektu do katalogu roboczego w kontenerze
COPY . .

# Uruchom aplikację
CMD ["python", "main.py"]
