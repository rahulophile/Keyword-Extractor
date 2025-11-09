import os
from flask import Flask, render_template, request, jsonify
from PIL import Image
import pytesseract
import PyPDF2
import spacy
import pytextrank # <--- यही है ज़रूरी लाइन जिसे जोड़ा गया है

# --- spaCy मॉडल लोड करना (अब यह काम करेगा) ---
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("textrank")
print("Model loaded successfully.")


# --- बाकी का कोड बिल्कुल वैसा ही रहेगा ---

def extract_text_from_image(image_file):
    try:
        image = Image.open(image_file)
        return pytesseract.image_to_string(image)
    except Exception as e:
        return None

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = "".join(page.extract_text() for page in pdf_reader.pages)
        return text if text.strip() else None
    except Exception as e:
        return None

def extract_keywords_advanced(text, num_keywords=15):
    if not text or len(text.strip()) < 100:
        return []
    doc = nlp(text)
    keywords = [phrase.text for phrase in doc._.phrases[:num_keywords]]
    entities = [ent.text for ent in doc.ents if ent.label_ in ('ORG', 'PERSON', 'GPE', 'PRODUCT')]
    combined_keywords = list(dict.fromkeys(keywords + entities))
    return combined_keywords[:num_keywords]

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
        elif input_type == 'image':
            image_file = request.files.get('file')
            if image_file:
                article_text = extract_text_from_image(image_file)
        elif input_type == 'pdf':
            pdf_file = request.files.get('file')
            if pdf_file:
                article_text = extract_text_from_pdf(pdf_file)

        if not article_text:
            return jsonify({'error': 'Could not extract any readable text from the source. Please check the file.'}), 400

        keywords = extract_keywords_advanced(article_text, num_keywords)
        
        if not keywords:
            return jsonify({'error': 'Text was found, but no significant keywords were identified. Try with a longer text.'}), 400

        return jsonify({'keywords': keywords})

    except Exception as e:
        return jsonify({'error': f'An unexpected server error occurred: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True)