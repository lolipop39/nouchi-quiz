import logging
import os
import random

import httpx
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("NOUCHI_API_BASE_URL", "").rstrip("/")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN est manquant.")

if not API_BASE_URL:
    raise RuntimeError("NOUCHI_API_BASE_URL est manquant.")


async def fetch_questions() -> list[dict]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(f"{API_BASE_URL}/questions")
        response.raise_for_status()
        return response.json()


def score(context: ContextTypes.DEFAULT_TYPE) -> dict[str, int]:
    return context.user_data.setdefault("score", {"correct": 0, "total": 0})


async def send_next_question(message, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        questions = await fetch_questions()
    except httpx.HTTPError:
        await message.reply_text("Le service de quiz est indisponible. Réessaie bientôt.")
        return

    used_ids = context.user_data.setdefault("used_question_ids", [])
    available = [item for item in questions if item["id"] not in used_ids]

    if not available:
        current_score = score(context)
        await message.reply_text(
            f"Quiz terminé ! Ton score final est {current_score['correct']}/{current_score['total']}.\n\n"
            "Envoie /quiz pour une nouvelle partie."
        )
        context.user_data["used_question_ids"] = []
        context.user_data["score"] = {"correct": 0, "total": 0}
        return

    question = random.choice(available)
    used_ids.append(question["id"])

    keyboard = [
        [InlineKeyboardButton(choice, callback_data=f"answer:{question['id']}:{index}")]
        for index, choice in enumerate(question["choices"])
    ]

    await message.reply_text(
        f"Question {len(used_ids)}/{len(questions)}\n\n{question['text']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message:
        await update.effective_message.reply_text(
            "Bienvenue sur Nouchi Quiz ! Envoie /quiz pour démarrer une partie."
        )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message:
        await send_next_question(update.effective_message, context)


async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not query or not query.data:
        return

    await query.answer()

    try:
        _, question_id_text, choice_index_text = query.data.split(":")
        question_id = int(question_id_text)
        choice_index = int(choice_index_text)
        questions = await fetch_questions()
        question = next(item for item in questions if item["id"] == question_id)
        choice = question["choices"][choice_index]

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/answers",
                json={"question_id": question_id, "choice": choice},
            )
            response.raise_for_status()
            result = response.json()
    except (httpx.HTTPError, IndexError, StopIteration, ValueError):
        await query.edit_message_text("Erreur de vérification. Envoie /quiz pour recommencer.")
        return

    current_score = score(context)
    current_score["total"] += 1

    if result["correct"]:
        current_score["correct"] += 1
        verdict = "Bonne réponse !"
    else:
        verdict = "Mauvaise réponse."

    await query.edit_message_text(
        f"{question['text']}\n\nTon choix : {choice}\n{verdict}\n"
        f"Score : {current_score['correct']}/{current_score['total']}"
    )

    await send_next_question(query.message, context)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CallbackQueryHandler(answer_callback, pattern=r"^answer:"))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
