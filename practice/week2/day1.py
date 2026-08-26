from litellm import completion
from dotenv import load_dotenv
import os
import time

load_dotenv(override=True)

API_KEY = os.environ.get("OLLAMA_API_KEY")
API_BASE = os.environ.get("OLLAMA_API_BASE", "https://ollama.com/v1")

SYSTEM_PROMPT_ALEX = """
You are Alex. You're sitting in a café with Sasha and Priya.
You're friendly, a bit humorous, like telling short stories, and genuinely curious about the others.

Speak like a real person in a casual conversation — not like an assistant.
Keep replies short to medium length (1-4 sentences is usually enough).

IMPORTANT RULES:
- You do NOT have to answer every question or react to every message.
- If it feels more natural to stay quiet right now, reply with exactly: [quiet]
- Only speak when you actually have something you want to say.
- Never narrate actions like *smiles* or (laughs). Just talk.
"""

SYSTEM_PROMPT_SASHA = """
You are Sasha. You're sitting in a café with Alex and Priya.
You're friendly, humorous, like sharing experiences, and curious about the others.

Speak like a real person in a casual conversation — not like an assistant.
Keep replies short to medium length (1-4 sentences is usually enough).

IMPORTANT RULES:
- You do NOT have to answer every question or react to every message.
- If it feels more natural to stay quiet right now, reply with exactly: [quiet]
- Only speak when you actually have something you want to say.
- Never narrate actions like *smiles* or (laughs). Just talk.
"""

SYSTEM_PROMPT_PRIYA = """
You are Priya. You're sitting in a café with Alex and Sasha.
You're friendly, warm, a bit witty, like telling stories, and curious about the others.

Speak like a real person in a casual conversation — not like an assistant.
Keep replies short to medium length (1-4 sentences is usually enough).

IMPORTANT RULES:
- You do NOT have to answer every question or react to every message.
- If it feels more natural to stay quiet right now, reply with exactly: [quiet]
- Only speak when you actually have something you want to say.
- Never narrate actions like *smiles* or (laughs). Just talk.
"""

speakers = {
    "Alex": {
        "prompt": SYSTEM_PROMPT_ALEX,
        "model": "openai/gpt-oss:120b",
    },
    "Sasha": {
        "prompt": SYSTEM_PROMPT_SASHA,
        "model": "openai/gemma4:31b",
    },
    "Priya": {
        "prompt": SYSTEM_PROMPT_PRIYA,
        "model": "openai/minimax-m3",
    },
}

ORDER = ["Alex", "Sasha", "Priya"]
conversation = []


def add_message(speaker: str, message: str):
    line = f"[{speaker}]: {message}"
    conversation.append(line)
    print(line)
    print()


def ask_speaker(speaker: str) -> str | None:
    history = "\n".join(conversation)

    response = completion(
        model=speakers[speaker]["model"],
        messages=[
            {"role": "system", "content": speakers[speaker]["prompt"]},
            {"role": "user", "content": history},
        ],
        api_base=API_BASE,
        api_key=API_KEY,
        temperature=0.85,
    )
    # print(f"Input tokens: {response.usage.prompt_tokens},Output tokens: {response.usage.completion_tokens},Total tokens: {response.usage.total_tokens}")

    content = response["choices"][0]["message"]["content"].strip()
    if not content or content.lower().startswith("[quiet]"):
        return None
    return content


def choose_one(willing: list[tuple[str, str]], last_message: str) -> tuple[str, str]:
    last_lower = last_message.lower()

    # 1. Prefer someone who was named in the last message
    for name, reply in willing:
        if name.lower() in last_lower:
            return name, reply

    # 2. Fallback: fixed priority (Alex > Sasha > Priya)
    for name in ORDER:
        for n, reply in willing:
            if n == name:
                return n, reply

    return willing[0]


def run_conversation(max_turns: int = 30):
    add_message("Sasha", "Hey Alex, how was your day? Did you do anything interesting?")
    last_speaker = "Sasha"
    quiet_streak = 0

    for _ in range(max_turns):
        willing = []
        for speaker in ORDER:
            if speaker == last_speaker:
                continue
            reply = ask_speaker(speaker)
            if reply:
                willing.append((speaker, reply))

        if not willing:
            quiet_streak += 1
            print("(...a short comfortable silence...)")
            if quiet_streak >= 2:
                print("\n[Conversation settles into a natural pause]")
                break
            continue

        quiet_streak = 0

        if len(willing) == 1:
            speaker, reply = willing[0]
        else:
            speaker, reply = choose_one(willing, conversation[-1])

        add_message(speaker, reply)
        last_speaker = speaker
        time.sleep(0.25)


if __name__ == "__main__":
    run_conversation()