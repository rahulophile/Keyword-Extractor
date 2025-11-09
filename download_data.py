import nltk
import ssl

# SSL सर्टिफ़िकेट एरर को ठीक करने के लिए (बहुत आम समस्या)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

print("NLTK डेटा डाउनलोड करना शुरू कर रहा हूँ...")

# हमें जिन पैकेजों की जरूरत है
packages_to_download = ['punkt', 'stopwords', 'punkt_tab']

for package in packages_to_download:
    try:
        print(f"-> '{package}' पैकेज डाउनलोड हो रहा है...")
        nltk.download(package)
        print(f"   '{package}' सफलतापूर्वक डाउनलोड हो गया।")
    except Exception as e:
        print(f"   '{package}' को डाउनलोड करने में एरर आया: {e}")

print("\nडाउनलोड प्रक्रिया पूरी हुई।")