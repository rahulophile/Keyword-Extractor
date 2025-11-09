# 1. बेस इमेज के रूप में एक हल्का Python चुनें
FROM python:3.11-slim

# 2. वर्किंग डायरेक्टरी सेट करें
WORKDIR /app

# 3. Tesseract और अन्य सिस्टम निर्भरताएँ इंस्टॉल करें
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. requirements.txt को कॉपी और इंस्टॉल करें
#    (अब यह spaCy मॉडल को भी इंस्टॉल करेगा)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. spaCy मॉडल डाउनलोड कमांड को हटा दिया गया है
#    (RUN python -m spacy download en_core_web_sm) <--- इस लाइन को हटा दें

# 6. बाकी का ऐप कोड (app.py, templates फोल्डर) कॉपी करें
COPY . .

# 7. Render को बताएं कि हमारा ऐप किस पोर्ट पर चलेगा
EXPOSE 10000

# 8. ऐप को Gunicorn सर्वर से शुरू करने की कमांड
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers=2", "--timeout=120", "app:app"]