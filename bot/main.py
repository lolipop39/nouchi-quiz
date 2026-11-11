import logging
import os

import httpx
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message:
        await update.effective_message.reply_text(
            "Bienvenue sur Nouchi Quiz ! Envoie /quiz pour commencer."
        )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return

    try:
        questions = await fetch_questions()
    except httpx.HTTPError:
        await update.effective_message.reply_text(
            "Le service de quiz est indisponible. Réessaie dans un instant."
        )
        return

    if not questions:
        await update.effective_message.reply_text("Aucune question disponible.")
        return

    question = questions[0]
    keyboard = [
        [
            InlineKeyboardButton(
                choice,
                callback_data=f"answer:{question['id']}:{index}",
            )
        ]
        for index, choice in enumerate(question["choices"])
    ]

    await update.effective_message.reply_text(
        question["text"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def answer_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
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
        await query.edit_message_text(
            "Impossible de vérifier cette réponse. Relance /quiz."
        )
        return

    verdict = "Bonne réponse !" if result["correct"] else "Mauvaise réponse."
    await query.edit_message_text(
        f"{question['text']}\n\n"
        f"Ton choix : {choice}\n"
        f"{verdict}"
    )


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CallbackQueryHandler(answer_callback, pattern=r"^answer:"))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
