import os
from dotenv import load_dotenv
from typing import Literal
from openai import OpenAI
from typing import Literal
import json
from practice.reusable.webscrapper import scrape_any_site_selenium

load_dotenv()


AI_BASE_URL = os.getenv('AI_BASE_URL', "https://generativelanguage.googleapis.com/v1beta/openai/")
# change the url to http://localhost:11434/v1 for use local ollama i have gemma 2b but i dont gonna use local as i dont need as of now

API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('OLLAMA_API_KEY')
# MODEL_NAME = "gemini-3.5-flash-lite"
MODEL_NAME = "gemma4:31b-cloud"

URL_EXTRACTION_SYSTEM_PROMPT = """
You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
You should respond in JSON as in this example:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""

def found_releavent_links(url):
    print("founding releavent links for the url: ", url)
    ai_ready_text, scraped_links = scrape_any_site_selenium(url)
    user_prompt = f"""
    Here is the list of links on the website {url} -
    Please decide which of these are relevant web links for a brochure about the company, 
    respond with the full https URL in JSON format.
    Do not include Terms of Service, Privacy, email links.
    
    Links (some might be relative links):
    
    """
    user_prompt += "\n".join(scraped_links)
    ollama = OpenAI(base_url=AI_BASE_URL, api_key=API_KEY)
    response = ollama.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": URL_EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )
    result = response.choices[0].message.content
    links = json.loads(result)
    print(f"Found {len(links['links'])} relevant links")
    return links
    

def fetch_page_and_all_relevant_links(url):
    contents = scrape_any_site_selenium(url)[0]
    relevant_links = found_releavent_links(url)
    result = f"## Landing Page:\n\n{contents}\n## Relevant Links:\n"
    for link in relevant_links['links']:
        result += f"\n\n### Link: {link['type']}\n"
        result += scrape_any_site_selenium(link["url"])[0]
    return result

if __name__ == "__main__":
    url = input("Enter the URL of the website to scrape: ")
    print(found_releavent_links(url))