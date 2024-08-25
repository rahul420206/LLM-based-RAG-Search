from flask import jsonify, request
from utils import search_articles, fetch_article_content, concatenate_content, generate_answer
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/query', methods=['POST'])
def query():
    try:
        query = request.json.get('query')
        if not query:
            return jsonify({"error": "No query provided"}), 400

        # Fetch articles
        articles = search_articles(query)
        print(f"Articles fetched: {articles}") 

        # Fetch content for each article
        for article in articles:
            article["content"] = fetch_article_content(article["url"])
            print(f"Fetched content for {article['url']}: {article['content']}") 

        # Check if any content was fetched
        if not any(article["content"] for article in articles):
            print("No content could be extracted from any of the articles.") 
            return jsonify({"answer": "Sorry, I couldn't find any relevant content."})

        # Concatenate content
        full_content = concatenate_content(articles)
        print(f"Full concatenated content: {full_content}") 

        # Generate an answer
        answer = generate_answer(full_content, query)
        print(f"Generated answer: {answer}") 

        return jsonify({"answer": answer})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An internal error occurred"}), 500


if __name__ == '__main__':
    app.run(host='localhost', port=5001, debug=True)
