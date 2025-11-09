# 1. बेस इमेज
FROM python:3.11-slim

# 2. वर्किंग डायरेक्टरी
WORKDIR /app

# 3. सिस्टम निर्भरताएँ (Tesseract और Git)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    git \
    && rm -rf /var/lib/apt/lists/*

# 4. Python निर्भरताएँ
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. बाकी का ऐप कोड कॉपी करें
COPY . .

# 6. Hugging Face के लिए सही पोर्ट को एक्सपोज करें
EXPOSE 7860

# 7. Gunicorn को सही पोर्ट पर शुरू करने की कमांड
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers=2", "--timeout=120", "app:app"]