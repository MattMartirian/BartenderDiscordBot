<<<<<<< HEAD
﻿import discord
from discord.ext import commands
import asyncio
import os
from flask import Flask, request, jsonify
from threading import Thread
import aiohttp

# Configuración del bot de Discord
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_CHANNEL_ID = 1312695472359735328  # Reemplaza con el ID de tu canal
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Evento cuando el bot se conecta
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send(f"¡El bot {bot.user.name} se ha iniciado exitosamente!")

# Función para enviar mensajes a Discord
async def send_to_discord(repo_name, action_type, branch, author, timestamp, title, description, commit_url):
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send(
            f"🚀 **Acción realizada en el repositorio `{repo_name}`**\n\n"
            f"**Tipo de acción:** `{action_type}`\n"
            f"**Branch afectada:** `{branch}`\n"
            f"**Commit Hash:** `{commit_url.split('/')[-1]}`\n"
            f"**Autor:** `{author}`\n"
            f"**Fecha:** `{timestamp}`\n\n"
            f"🔹 **Título del commit:** {title}\n"
            f"🔹 **Descripción:** {description}\n\n"
            f"🔗 **Enlace al commit:** [Ver commit en GitHub]({commit_url})"
        )

# Función para iniciar el bot de Discord
async def start_discord_bot():
    await bot.start(DISCORD_TOKEN)

# Configuración de Flask
=======
from flask import Flask, request, jsonify
import asyncio
from threading import Thread
import discord_bot  # Asegúrate de que este módulo contiene tus funciones de Discord, como send_to_discord

# Crear la aplicación Flask
>>>>>>> 092989eb7e503d7fcf826e0e9832dbbd7481376a
app = Flask(__name__)

# Webhook de GitHub
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # Extraer información del payload
    repo_name = data['repository']['name']
    action_type = data.get('action', 'Push')
    branch = data['ref'].split('/')[-1]

    for commit in data['commits']:
        author = commit['author']['name']
        timestamp = commit['timestamp']
        title = commit['message'].split("\n")[0]
        description = "\n".join(commit['message'].split("\n")[1:]) if len(commit['message'].split("\n")) > 1 else "*No se ha brindado una descripción*"
        commit_url = commit['url']

        # Enviar mensaje al canal de Discord
        asyncio.run_coroutine_threadsafe(
            send_to_discord(repo_name, action_type, branch, author, timestamp, title, description, commit_url),
            bot.loop
        )

    return jsonify({"status": "success"}), 200

# Función para iniciar Flask en un hilo separado
def start_flask():
    app.run(host="0.0.0.0", port=8080)

# Función para iniciar el bot de Discord
def start_discord_bot():
    asyncio.run(discord_bot.start_discord_bot())

# Función principal para iniciar todo
def main():
    # Iniciar Flask en un hilo separado
    flask_thread = Thread(target=start_flask)
    flask_thread.start()

<<<<<<< HEAD
    # Iniciar ping
    asyncio.run(ping_self())

    # Iniciar el bot de Discord
    asyncio.run(start_discord_bot())
=======
    # Iniciar el bot de Discord en un hilo separado
    discord_thread = Thread(target=start_discord_bot)
    discord_thread.start()
>>>>>>> 092989eb7e503d7fcf826e0e9832dbbd7481376a

if __name__ == "__main__":
    main()
