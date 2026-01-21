import wikipediaapi
import requests
import time

wiki = wikipediaapi.Wikipedia(language="en", user_agent="llm10-lab")

def web_search(query: str) -> str:
    time.sleep(0.2)
    page = wiki.page(query)
    return page.summary[:500] if page.exists() else "No result."

def fetch_url(url: str) -> str:
    time.sleep(0.2)
    return requests.get(url, timeout=5).text[:1000]

def calculator(expression: str) -> str:
    return str(eval(expression))
