import google.generativeai as genai
from app.config.settings import Settings
from typing import Dict, List, Optional


settings = Settings()
genai.configure(api_key=settings.GEMINI_API_KEY)


model = genai.GenerativeModel("gemini-1.5-flash")

conversation_history: Dict[str, List[Dict[str, str]]] = {}

BOT_INTRODUCTION = ("Hi! I am a translation bot that can help you translate text across languages. "
                    "Simply send me the text you'd like to translate, and I'll help you right away.")

async def get_ai_response(prompt: str, user_id: str) -> str:
    try:

        is_first_message = user_id not in conversation_history

        if is_first_message:
            conversation_history[user_id] = []
            conversation_history[user_id].append({"role": "user", "parts": [prompt]})
            conversation_history[user_id].append({"role": "model", "parts": [BOT_INTRODUCTION]})
            return BOT_INTRODUCTION

        conversation_history[user_id].append({"role": "user", "parts": [prompt]})

        # if user_id not in conversation_history:
        #     conversation_history[user_id] = []

        chat = model.start_chat(history=conversation_history[user_id])

        response = await chat.send_message_async(prompt)

        response_text = response.text

        formatted_text = response_text.replace('\n', '')

        conversation_history[user_id].append({"role": "model", "parts": [response_text]})

        # response = await model.generate_content_async(prompt)

        return formatted_text
    except Exception as e:
        print(f"[AI Error] {e}")
        return "Sorry, I'm having trouble processing your request right now."