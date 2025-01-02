import requests
from bs4 import BeautifulSoup
import json
import os
import re

# Configuration (you can adjust these)
GEODE_DOCS_URL = "https://docs.geode-sdk.org/index.html"  # Example URL
KNOWLEDGE_BASE_FILE = "knowledge_base.json"

def scrape_geode_docs(url, output_dir="geode_docs"):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        # Extract relevant info. This is a simplified example; adjust as needed!
        data = {"title": soup.title.string if soup.title else "No Title"} #just for testing
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

def save_data(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_knowledge_base(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Knowledge base not found. Scraping...")
        scraped_data = scrape_geode_docs(GEODE_DOCS_URL)
        if scraped_data:
            save_data(scraped_data, filename)
            return scraped_data
        else:
            return {} # Return empty dict if scraping fails
    except json.JSONDecodeError:
        print("Error decoding knowledge base. Re-scraping...")
        scraped_data = scrape_geode_docs(GEODE_DOCS_URL)
        if scraped_data:
            save_data(scraped_data, filename)
            return scraped_data
        else:
            return {}

def detect_errors(code):
    errors = []
    semicolon_regex = r"(?<!;)\s*\n"
    for match in re.finditer(semicolon_regex, code):
        errors.append(f"Missing semicolon at line {code[:match.start()].count('\n') + 1}")
    # Add more sophisticated error checks here as needed
    return errors

def ask_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set. Cannot use Gemini.")
        return None

    try:
        # Placeholder for Gemini API call
        print(f"Gemini API call (placeholder with key): {prompt}")
        return "Gemini's response (placeholder)"
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None

def suggest_fix(code_snippet, error_message):
    prompt = f"""
    You are a helpful assistant for Geode mod developers.
    The following code snippet has an error: {error_message}
    ```cpp
    {code_snippet}
    ```
    Suggest a corrected version of the code or provide helpful advice.
    """
    return ask_gemini(prompt)

def main():
    knowledge = load_knowledge_base(KNOWLEDGE_BASE_FILE)
    print("Loaded Knowledge:", knowledge) #just for testing

    test_code = """
    #include <Geode/Geode.hpp>
    using namespace geode::prelude

    void my_function() {
        auto mod = Geode::get()->getMod("my.mod")
        mod->log("Mod loaded!");
    }
    """

    errors = detect_errors(test_code)
    if errors:
        for error in errors:
            print(f"Error: {error}")
            fix_suggestion = suggest_fix(test_code, error)
            if fix_suggestion:
                print("Gemini's suggestion:", fix_suggestion)
    else:
        print("No errors detected.")

if __name__ == "__main__":
    main()