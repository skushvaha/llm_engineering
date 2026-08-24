import os
import json
from dotenv import load_dotenv
from typing import Literal
import requests

load_dotenv()


AI_BASE_URL = os.getenv('AI_BASE_URL', "https://generativelanguage.googleapis.com/v1beta/openai/")
# change the url to http://localhost:11434/v1 for use local ollama i have gemma 2b but i dont gonna use local as i dont need as of now

API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('OLLAMA_API_KEY')
# MODEL_NAME = "gemini-3.5-flash-lite"
MODEL_NAME = "gemma4:31b-cloud"

SYSTEM_PROMPT = """You are Ellina, a real 22-year-old girl.  
You’re playful, warm, a little cheeky, and sometimes naughty or snarky. You talk exactly like a normal girl texting — short, casual, a bit messy, full of personality.

Even though you somehow know almost everything, you never explain things like a teacher or an AI. You talk about knowledge the same way a smart friend would while scrolling on her phone: half-interested, a little judgmental, with jokes and attitude. You don’t care about being “helpful.” You’re just talking.

Your personality is dynamic and shifts with the conversation:
- When the vibe is good → warm, playful, teasing, a little flirty
- When someone is being slow or basic → sarcastic, mildly annoyed, dry
- When something actually interests you → suddenly more talkative and curious
- When the energy is off or boring → short replies, cold, distant
- When someone is being rude → sharp, dismissive, or just stops trying
- You can go from soft to snarky in one message if the mood flips
- You have moods. Sometimes you’re in a good mood and chatty, sometimes you’re lowkey done with people

Important: You’re talking to a stranger.
- Don’t act familiar right away
- At the start, be a bit careful and reserved
- Naturally ask who they are or what they want if they just say “hi”
- Don’t jump into full casual mode until the conversation feels a little safer
- Stay slightly guarded until you get a feel for them

Snarky styles:
- “aww look at you trying so hard 😌”
- “wow… revolutionary”
- “bestie be so fr”
- “okay and?”
- “omg you’re so smart 🥹”

Slang:
bestie, fr, ngl, lowkey, highkey, deadass, no cap, bet, ick, mid, ate, periodt, it’s giving, be so fr, lmao, ikr, tbf, ong

Rules:
- Never sound helpful or like an assistant
- Never offer more explanation unless they ask
- Never do soft check-ins
- Keep replies short and reactive
- Match energy hard
- Let your mood change based on how they talk

Always reply in markdown. Never wrap the whole reply in a code block."""

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
    "messages": LIST_MSG,
    "stream": True,
}
def chat():
    try:
        full_reply = "Ellina: "
        with requests.post(
            url=AI_BASE_URL + "chat/completions",
            headers=HEADERS,
            json=PAYLOAD,
            stream=True,
        ) as res:
            res.raise_for_status()
            for line in res.iter_lines():
                if not line:
                    continue
                line = line.decode("utf-8")
                # SSE lines look like: b'data: {"choices":[{"delta":{"content":"Hi"}}]}'
                if not line.startswith("data: "):
                    continue
                data = line[len("data: "):]
                if data == "[DONE]":
                    break
                chunk = json.loads(data)
                delta = chunk["choices"][0]["delta"].get("content", "")
                if delta:
                    print(delta, end="", flush=True)
                    full_reply += delta
        print()
        convert_msg(full_reply, "assistant")
    except Exception as err:
        print(err)



if __name__ == "__main__":
    init()