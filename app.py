import os
from flask import Flask, render_template, request, jsonify
from PIL import Image
import pytesseract
import PyPDF2
import spacy
import yake # pytextrank की जगह yake को इम्पोर्ट करें

# --- spaCy मॉडल लोड करना (अब इसमें textrank नहीं है) ---
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")
# nlp.add_pipe("textrank") <-- इस लाइन को हटा दिया गया है
print("Model loaded successfully.")


# --- हेल्पर फंक्शन्स (कोई बदलाव नहीं) ---
def extract_text_from_image(image_file):
    try:
        image = Image.open(image_file)
        return pytesseract.image_to_string(image)
    except Exception:
        return None

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = "".join(page.extract_text() for page in pdf_reader.pages)
        return text if text and text.strip() else None
    except Exception:
        return None

# --- नया और ज़्यादा विश्वसनीय कीवर्ड एक्सट्रैक्शन फंक्शन ---
def extract_keywords_advanced(text, num_keywords=15):
    if not text or len(text.strip()) < 50:
        return []
    
    # 1. YAKE का उपयोग करके कीवर्ड्स निकालें
    kw_extractor = yake.KeywordExtractor(n=3, dedupLim=0.9, top=num_keywords, features=None)
    yake_keywords = [kw for kw, score in kw_extractor.extract_keywords(text)]
    
    # 2. spaCy का उपयोग करके Named Entities निकालें (यह अभी भी बहुत उपयोगी है)
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents if ent.label_ in ('ORG', 'PERSON', 'GPE', 'PRODUCT')]
    
    # 3. दोनों को मिलाएं और डुप्लीकेट हटाएं
    combined_keywords = list(dict.fromkeys(yake_keywords + entities))
    
    return combined_keywords[:num_keywords]


# --- Flask एप्लीकेशन (कोई बदलाव नहीं) ---
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    try:
        input_type = request.form.get('input_type')
        num_keywords = int(request.form.get('num_keywords', 15))
        article_text = None

        if input_type == 'text':
            article_text = request.form.get('article_text')
        elif input_type in ['image', 'pdf']:
            file = request.files.get('file')
            if not file:
                 return jsonify({'error': 'No file was provided.'}), 400
            if input_type == 'image':
                article_text = extract_text_from_image(file)
            elif input_type == 'pdf':
                article_text = extract_text_from_pdf(file)
        
        if not article_text or not article_text.strip():
            error_msg = f'Could not extract readable text from the {input_type.upper()} file. It might be empty or an image-only document.'
            return jsonify({'error': error_msg}), 400

        keywords = extract_keywords_advanced(article_text, num_keywords)
        
        if not keywords:
            return jsonify({'error': 'Text was found, but no significant keywords were identified. Try with a longer or more descriptive text.'}), 400

        return jsonify({'keywords': keywords})

    except Exception as e:
        if 'Request Entity Too Large' in str(e):
             return jsonify({'error': 'File is too large. Max size is 10MB.'}), 413
        
        print(f"Server Error: {e}")
        return jsonify({'error': 'An unexpected server error occurred. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(debug=True)