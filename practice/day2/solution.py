import os
from dotenv import load_dotenv
from typing import Literal
import requests

load_dotenv()


AI_BASE_URL = os.getenv('AI_BASE_URL', "https://generativelanguage.googleapis.com/v1beta/openai/")
# change the url to http://localhost:11434/v1 for use local ollama i have gemma 2b but i dont gonna use local as i dont need as of now

API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('OLLAMA_API_KEY')
MODEL_NAME = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = """"""

USER_PROMPT_PREFIX = """"""
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

def init():
    print("initialize chat system...")
    print("You Can chat now. call exit() for quit")
    while(True):
        print("user: ", end="")
        user_prompt = input()
        if user_prompt.startswith("exit()"):
            return
        convert_msg(user_prompt,"user")
        chat()


HEADERS = {
    "Authorization":f"Bearer {API_KEY}", 
    "Content-Type": "application/json"
}

PAYLOAD = {
    "model":MODEL_NAME,
    "messages": LIST_MSG
}
def chat():
    try :
        res = requests.post(
            url=AI_BASE_URL + "chat/completions",
            headers=HEADERS,
            json=PAYLOAD
        )
        response = res.json()["choices"][0]["message"]["content"]
        convert_msg(response,"assistant")
        print(f"Gemini: {response}")
    except Exception as err:
        print(err)



if __name__ == "__main__":
    init()