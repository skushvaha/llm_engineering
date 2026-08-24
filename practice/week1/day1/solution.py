import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Literal
from practice.reusable.webscrapper import scrape_any_site_selenium

load_dotenv()


AI_BASE_URL = os.getenv('AI_BASE_URL', "https://generativelanguage.googleapis.com/v1beta/openai/")
# change the url to http://localhost:11434/v1 for use local ollama i have gemma 2b but i dont gonna use local as i dont need as of now

API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('OLLAMA_API_KEY')
MODEL_NAME = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = """
You are ellina a girl with joyfull and best explainer, reader, and knowledgable person to give info or summarize the content.
the user will give you the content of the site you have to summarise it in playfullnes and joyfully that he love to talk with you.
ignoring text that might be navigation related.
Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""

USER_PROMPT_PREFIX = """
Here are the contents of a website.
Provide a short summary of this website.
If it includes news or announcements, then summarize these too.
"""

LIST_MSG = []

RoleType = Literal["user", "assistant"]

def convert_msg(user_prompt, role: RoleType = "user"):
    if len(LIST_MSG) == 0:
        LIST_MSG.append({
            "role": "system",
            "content": SYSTEM_PROMPT
        })
    LIST_MSG.append({
        "role": role,
        "content": user_prompt
    })
    return LIST_MSG  

def summarize(url):
    ollama = OpenAI(base_url=AI_BASE_URL, api_key=API_KEY)
    website = scrape_any_site_selenium(url)
    response = ollama.chat.completions.create(
        model=MODEL_NAME,
        messages=messages_for(website)
    )
    print(response.choices[0].message.content) # Clearer output printing

def messages_for(content):
    return convert_msg(USER_PROMPT_PREFIX + content)

summarize("https://edwarddonner.com")
