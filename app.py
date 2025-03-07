from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import wikipediaapi
from deep_translator import GoogleTranslator  # Import translation library

app = Flask(__name__, template_folder=".")  # Serve index.html from the current directory
CORS(app)  # Enable CORS for frontend requests

def translate_text(text, src_lang, target_lang):
    """Translates text from source language to target language."""
    try:
        return GoogleTranslator(source=src_lang, target=target_lang).translate(text)
    except Exception as e:
        print(f"Translation failed: {e}")
        return text  # Return original text if translation fails

def get_wikipedia_summary(topic, language):
    """Fetches Wikipedia summary, prioritizing the requested language, then English, then translation."""
    user_agent = "MyWikipediaBot/1.0 (myemail@example.com)"
    wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language=language)

    # Step 1: Try Wikipedia in the requested language
    page = wiki.page(topic)
    if page.exists():
        return page.summary  

    # Step 2: Translate topic to English and check English Wikipedia
    translated_topic = translate_text(topic, language, "en")
    print(f"Translated '{topic}' ({language}) to '{translated_topic}' (en)")

    wiki_en = wikipediaapi.Wikipedia(user_agent=user_agent, language="en")
    page_en = wiki_en.page(translated_topic)
    if page_en.exists():
        print("Found summary in English. Translating back to", language)
        return translate_text(page_en.summary, "en", language)  # Translate summary back to requested language

    # Step 3: Try translating back and searching again in original language
    translated_back = translate_text(translated_topic, "en", language)
    print(f"Re-translated '{translated_topic}' (en) to '{translated_back}' ({language})")

    page_back = wiki.page(translated_back)
    if page_back.exists():
        return page_back.summary  

    # Step 4: If no results, return an error message
    return "No summary found in any language."

@app.route("/")
def index():
    return render_template("index.html")  # Serve the frontend

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    topic = data.get("topic")
    language = data.get("language", "en")

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    summary = get_wikipedia_summary(topic, language)
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug=True)
