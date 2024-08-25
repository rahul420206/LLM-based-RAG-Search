import os
import requests
import json
from bs4 import BeautifulSoup
import cohere
from dotenv import load_dotenv

load_dotenv()
co = cohere.Client('evLatt2FuOBOJti8orWXbEoATx0NDUTGAkLcXRJO')


SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def search_articles(query):
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": query,
            "gl": "in"  
        })
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)

        print(f"Serper API Response Status Code: {response.status_code}")
        print(f"Serper API Response Text: {response.text}")

        if response.status_code == 200:
            data = response.json()
            articles = [
                {"url": item["link"], "title": item["title"], "snippet": item["snippet"]}
                for item in data.get("organic", [])
            ]
            print(f"Articles: {articles}")
            return articles
        else:
            if response.status_code == 403:
                raise Exception("Unauthorized. Please check your Serper API key.")
            else:
                raise Exception(f"Serper API Error: {response.status_code}")
    except Exception as e:
        print(f"Error in search_articles: {e}")
        return {"error": str(e)}

def fetch_article_content(url):
    try:
        response = requests.get(url)
        print(f"Fetching URL: {url}")
        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            content = " ".join([p.get_text() for p in soup.find_all(["h1", "h2", "p"])])
            print(f"Content for URL {url}: {content}")
            return content.strip()
        else:
            print(f"Error fetching article content: {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error in fetch_article_content: {e}")
        return ""

def concatenate_content(articles):
    try:
        full_text = "\n\n".join(article.get("content", "") for article in articles if article.get("content"))
        print(f"Full Concatenated Content: {full_text}")
        return full_text
    except Exception as e:
        print(f"Error in concatenate_content: {e}")
        return ""

def generate_answer(content, query):
    if not content:
        return "Sorry, I couldn't find any relevant content."
    
    try:
        prompt = f"User query: {query}\n\nRelevant content:\n{content}"
        response = co.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        answer = response.generations[0].text.strip()
        return answer
    except Exception as e:
        print(f"Error in generate_answer: {e}")
        return f"An error occurred while generating the response: {str(e)}"
