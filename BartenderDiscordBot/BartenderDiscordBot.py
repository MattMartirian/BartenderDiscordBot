import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import asyncio
import aiohttp
from threading import Thread
import os

# Configuración del bot
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuración de Flask
app = Flask(__name__)

# Canal de Discord donde enviar los mensajes
DISCORD_CHANNEL_ID = 1312695472359735328  # Reemplaza con el ID de tu canal
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Indicadores de estado
bot_ready = False
pending_webhooks = []  # Lista para almacenar webhooks en espera

# Webhook de GitHub
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # Agregar el webhook a la lista pendiente
    pending_webhooks.append(data)

    # Si el bot ya está listo, procesar el webhook inmediatamente
    if bot_ready:
        asyncio.run_coroutine_threadsafe(process_webhook(data), bot.loop)
    
    return jsonify({"status": "success"}), 200

async def process_webhook(webhook_data):
    """
    Procesa un webhook de GitHub y envía un mensaje al canal de Discord.
    """
    repo_name = webhook_data['repository']['name']
    action_type = webhook_data.get('action', 'Push')
    branch = webhook_data['ref'].split('/')[-1]

    for commit in webhook_data.get('commits', []):
        author = commit['author']['name']
        timestamp = commit['timestamp']
        title = commit['message'].split("\n")[0]
        description = "\n".join(commit['message'].split("\n")[1:]) if len(commit['message'].split("\n")) > 1 else "*No se ha brindado una descripción*"
        commit_url = commit['url']

        # Enviar el mensaje al canal de Discord
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            await channel.send(
                f"🚀 **Acción en {repo_name}**\n"
                f"**Tipo de acción:** {action_type}\n"
                f"**Branch:** {branch}\n"
                f"**Autor:** {author}\n"
                f"**Fecha:** {timestamp}\n"
                f"**Título:** {title}\n"
                f"**Descripción:** {description}\n"
                f"🔗 [Commit Link]({commit_url})"
            )


# Iniciar Flask en un hilo separado
def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Evento de inicio del bot
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

    # Enviar mensaje inicial al canal de Discord
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send(f"¡El bot {bot.user.name} se ha iniciado exitosamente! Tengo {len(pending_webhooks)} webhook(s) pendiente(s).")

    # Procesar los webhooks pendientes
    while pending_webhooks:
        webhook_data = pending_webhooks.pop(0)
        await process_webhook(webhook_data)

# Función principal
async def main():
    # Iniciar Flask en un hilo separado
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Iniciar el bot
    await bot.start(DISCORD_TOKEN)

# Ejecutar la función principal
asyncio.run(main())
