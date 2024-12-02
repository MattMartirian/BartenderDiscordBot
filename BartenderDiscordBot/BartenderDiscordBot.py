import discord
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

# Función para hacer ping a la aplicación Flask
async def ping_self():
    url = "http://127.0.0.1:8080"
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    print(f"Ping exitoso: {response.status}")
        except Exception as e:
            print(f"Error al hacer ping: {e}")
        await asyncio.sleep(300)  # Cada 5 minutos

# Función para iniciar Flask en un hilo separado
def start_flask():
    app.run(host="0.0.0.0", port=8080)

# Función principal para iniciar todo
def main():
    # Iniciar Flask en un hilo
    flask_thread = Thread(target=start_flask)
    flask_thread.start()

    # Iniciar ping
    asyncio.run(ping_self())

    # Iniciar el bot de Discord
    asyncio.run(start_discord_bot())

if __name__ == "__main__":
    main()
