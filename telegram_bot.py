import os
import asyncio
import logging
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
MODEL = "openai/gpt-oss-120b:free"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

tavily = TavilyClient(api_key=TAVILY_API_KEY)

historico = {}

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = (
    "Você é um assistente simpático e informal. "
    "Responda sempre em português brasileiro. "
    "Guarde informações do cotidiano que o usuário te contar e use isso nas respostas. "
    "Seja direto e descontraído."
)


PALAVRAS_WEB = [
    "hoje", "agora", "atual", "atualmente", "notícia", "noticia",
    "preço", "preco", "valor", "clima", "tempo", "temperatura",
    "quando foi", "quem é", "quem e", "o que é", "o que e",
    "novidade", "lançamento", "lancamento", "resultado", "placar",
    "jogo", "eleição", "eleicao", "guerra", "aconteceu", "acontecendo",
]

def precisa_buscar_web(pergunta: str) -> bool:
    texto = pergunta.lower()
    return any(p in texto for p in PALAVRAS_WEB)


def buscar_web(query: str) -> str:
    resposta = tavily.search(query=query, max_results=3)
    resultados = [f"- {r['title']}: {r['content']}" for r in resposta.get("results", [])]
    return "\n".join(resultados) if resultados else "Nenhum resultado encontrado."


def perguntar_ia(chat_id: int, mensagem_usuario: str) -> str:
    if chat_id not in historico:
        historico[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    historico[chat_id].append({"role": "user", "content": mensagem_usuario})

    if precisa_buscar_web(mensagem_usuario):
        resultados = buscar_web(mensagem_usuario)
        historico[chat_id].append({
            "role": "system",
            "content": f"Resultados da busca na web:\n{resultados}",
        })

    resposta = client.chat.completions.create(
        model=MODEL,
        messages=historico[chat_id],
    )

    if not resposta.choices:
        return "Desculpe, não consegui gerar uma resposta agora. Tente de novo."

    texto_resposta = resposta.choices[0].message.content
    if not texto_resposta:
        return "Desculpe, não consegui gerar uma resposta agora. Tente de novo."
    texto_resposta = texto_resposta.strip()
    historico[chat_id].append({"role": "assistant", "content": texto_resposta})

    return texto_resposta


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Oi! Pode falar, tô aqui.")


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    mensagem = update.message.text

    stop_typing = asyncio.Event()

    async def manter_typing():
        while not stop_typing.is_set():
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(4)

    typing_task = asyncio.create_task(manter_typing())

    try:
        resposta = await asyncio.to_thread(perguntar_ia, chat_id, mensagem)
        limite = 4096
        for i in range(0, len(resposta), limite):
            await update.message.reply_text(resposta[i:i + limite])
    except Exception as e:
        logging.error(f"Erro ao responder: {e}")
        await update.message.reply_text("Tive um problema aqui, tenta de novo.")
    finally:
        stop_typing.set()
        typing_task.cancel()


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    print("Bot rodando...")
    app.run_polling()


if __name__ == "__main__":
    main()
