import os
import requests
from dotenv import load_dotenv
import tiktoken

from lexicon.lexicon import BASIC_PROMT, SUMMARY_PROMT
from promt.create_db import get_messages, delete_messages_by_chat_id, save_message

load_dotenv()

AI_API_KEY = os.getenv('AI_API_KEY')
HF_TOKEN = os.getenv('HF_TOKEN')
MODEL_NAME = os.getenv('MODEL_NAME')

MAX_CONTEXT_TOKENS = 2000
MAX_NEW_TOKENS = 256
SUMMARY_TRIGGER_TOKENS = 1800
SUMMARY_CHUNK_MESSAGES = 50

enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(enc.encode(text))


def get_ai_response(user_message):
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
        "X-Title": "TelegramBot"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        raise RuntimeError(f"OpenRouter error {response.status_code}: {response.text}")

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        raise RuntimeError(f"Unexpected response format: {data}")


def build_context_for_chat(chat_id: int) -> str:
    """
    Берёт сообщения для chat_id с конца, аккумулирует пока не достигнет MAX_CONTEXT_TOKENS.
    Возвращает готовый контекст для промпта.
    """
    messages = get_messages(chat_id)
    selected = []
    total_tokens = 0
    system_messages = [message for message in messages if message["role"] == "system"]
    system_text = ""
    if system_messages:
        system_text = "\n".join([m["text"] for m in system_messages])
        total_tokens += count_tokens(system_text)

    for message in reversed(messages):
        if message["role"] == "system":
            continue
        piece = f"{message['role'].upper()}: {message['text']}\n"
        piece_tokens = count_tokens(piece)
        if total_tokens + piece_tokens > MAX_CONTEXT_TOKENS:
            break
        selected.append(piece)
        total_tokens += piece_tokens

    selected.reverse()
    context_parts = []
    if system_text:
        context_parts.append("SYSTEM_SUMMARY:\n" + system_text)
    context_parts.extend(selected)
    return "\n".join(context_parts)


def _strip_prompt_prefix(output: str, prompt: str) -> str:
    """
    Если модель вернула весь prompt + продолжение, убирает prompt.
    """
    if not output:
        return ""
    out = output.strip()
    if out.startswith(prompt):
        return out[len(prompt):].strip()
    normalized_out = " ".join(out.split())
    normalized_prompt = " ".join(prompt.split())
    if normalized_out.startswith(normalized_prompt):
        return normalized_out[len(normalized_prompt):].strip()
    return out


def summarize_old_messages(chat_id: int):
    """
    Берёт самые старые сообщения, формирует суммарный текст и заменяет их на system-сообщение с кратким summary.
    """
    messages = get_messages(chat_id)
    total = 0
    for message in messages:
        total += count_tokens(message["text"])
    if total < SUMMARY_TRIGGER_TOKENS:
        return

    old_messages = [message for message in messages if message["role"] in ("user", "assistant")]
    old_to_summarize = old_messages[:SUMMARY_CHUNK_MESSAGES]
    if not old_to_summarize:
        return

    dialog_text = ""
    for message in old_to_summarize:
        dialog_text += f"{message['role'].upper()}: {message['text']}\n"

    summarization_prompt = (SUMMARY_PROMT + f"Диалог:\n{dialog_text}\n\nРезюме:")

    out = get_ai_response(summarization_prompt)
    summary = _strip_prompt_prefix(out, summarization_prompt)
    if not summary:
        summary = "Краткое резюме диалога (техническое): сохранены ключевые вопросы и ответы."

    delete_messages_by_chat_id(chat_id)
    save_message(chat_id, "system", "Резюме предыдущих сообщений: " + summary)


def generate_response_for_chat(chat_id: int, user_text: str) -> str:
    save_message(chat_id, "user", user_text)
    summarize_old_messages(chat_id)
    context = build_context_for_chat(chat_id)
    prompt = (BASIC_PROMT + f"КОНТЕКСТ:\n{context}\n\nВОПРОС: {user_text}\nОТВЕТ:")
    out = get_ai_response(prompt)
    generated = _strip_prompt_prefix(out, prompt)
    save_message(chat_id, "assistant", generated)
    return generated
