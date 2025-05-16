import os
import re  # regular expression
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load .env variables
load_dotenv()

# Clean and validate environment variables
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "").strip()
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "").strip()
os.environ["LANGCHAIN_TRACING_V2"] = "true"

groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
telegram_api_key = os.getenv("TELEGRAM_API_KEY", "").strip()

# Safety checks
if not groq_api_key:
    raise ValueError("Missing or invalid GROQ_API_KEY")
if not os.environ["LANGCHAIN_API_KEY"]:
    raise ValueError("Missing or invalid LANGCHAIN_API_KEY")
if not telegram_api_key:
    raise ValueError("Missing or invalid TELEGRAM_API_KEY")


# Joke generation chain using LangChain + Groq
def setup_llm_chain(topic="technology"):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a joke generating assistant. Generate only ONE joke on the given topic and do not continue the conversation"),
        ("user", f"Generate a joke on the topic: {topic}")
    ])

    llm = ChatGroq(
        model="Gemma2-9b-It",
        groq_api_key=groq_api_key
    )

    return prompt | llm | StrOutputParser()


# Bot command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Mention me with a topic like '@Binary_Joke_Bot python' to get a joke.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Mention me with a topic like '@Binary_Joke_Bot python' to get a funny joke.")


async def generate_joke(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    await update.message.reply_text(f"Generating a joke about {topic}...")
    joke = setup_llm_chain(topic).invoke({}).strip()
    await update.message.reply_text(joke)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    bot_username = context.bot.username

    if f'@{bot_username}' in msg:
        match = re.search(f'@{bot_username}\\s+(.*)', msg)
        if match and match.group(1).strip():
            await generate_joke(update, context, match.group(1).strip())
        else:
            await update.message.reply_text("Please specify a topic after mentioning me.")


# Main bot startup
def main():
    app = Application.builder().token(telegram_api_key).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
