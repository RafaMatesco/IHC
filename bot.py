import telebot
import sqlite3
from database import create_ecommerce_database
from ai_engine import generator

# 1. Garante que o banco de dados e as tabelas existam localmente
create_ecommerce_database()

# 2. Insira o token que você pegou com o @BotFather no Telegram
TOKEN_TELEGRAM = "7851874115:AAHvFFM2usaWD_EsXKI0blSs_r5QKvar-_8"
bot = telebot.TeleBot(TOKEN_TELEGRAM)

@bot.message_handler(commands=['start', 'help'])
def enviar_boas_vindas(message):
    boas_vindas = (
        "Olá! Eu sou o assistente do seu Banco de Dados E-commerce. 📊\n\n"
        "Pode me fazer perguntas em linguagem natural como:\n"
        "• 'Qual o produto mais caro?'\n"
        "• 'Quantos clientes estão cadastrados?'"
    )
    bot.reply_to(message, boas_vindas)

@bot.message_handler(func=lambda message: True)
def processar_pergunta(message):
    bot.send_chat_action(message.chat.id, 'typing')
    pergunta_usuario = message.text
    conn = sqlite3.connect("ecommerce.db")
    
    try:
        resposta_ia = generator(question=pergunta_usuario, conn=conn)
        
        if resposta_ia.error:
            resposta_final = f"❌ Erro ao processar a query SQL gerada:\n`{resposta_ia.error}`"
        else:
            # Agora priorizamos a resposta em texto natural gerada pelo Llama!
            # E deixamos o SQL embaixo como um detalhe técnico (opcional)
            resposta_final = (
                f"💬 {resposta_ia.text_answer}\n\n"
                f"⚙️ _[Logs técnicos]:_ \n"
                f"• *SQL executado:* `{resposta_ia.sql_query}`\n"
                f"• *Dados brutos:* `{resposta_ia.results}`"
            )
            
    except Exception as e:
        resposta_final = f"⚠️ Ocorreu um erro inesperado: {str(e)}"
    finally:
        conn.close()
        
    bot.reply_to(message, resposta_final, parse_mode="Markdown")


if __name__ == "__main__":
    print("🤖 Bot de IHC iniciado e aguardando perguntas...")
    bot.polling(none_stop=True)