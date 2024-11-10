from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import Counter
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/analyze', methods=['POST'])
def analyze_url():
    data = request.json
    url = data.get('url')
    top_n = data.get('top_n', 10)  # Default to top 10 words if not provided

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Add a user-agent header to mimic a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
        }
        
        # Fetch the content of the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an error if the response code is not 200
        content = response.text

        # Use BeautifulSoup to parse HTML and extract text content
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()

        # Use regex to find all words and convert them to lowercase
        words = re.findall(r'\b\w+\b', text.lower())

        # Calculate word frequency using Counter
        word_counts = Counter(words)
        top_words = word_counts.most_common(top_n)

        # Format results as a list of dictionaries
        results = [{"word": word, "frequency": freq} for word, freq in top_words]
        return jsonify(results)

    except requests.exceptions.RequestException as e:
        # Log error details to the console for debugging
        print(f"Error fetching URL: {e}")
        return jsonify({"error": "Failed to fetch content from the URL. Please try another URL or check if the site is accessible."}), 500

    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred while processing the request."}), 500

if __name__ == '__main__':
    app.run(debug=True)
