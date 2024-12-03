import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import asyncio
from threading import Thread, Event
import os

# Configuración del bot
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuración de Flask
app = Flask(__name__)

# Canal de Discord donde enviar los mensajes
DISCORD_CHANNEL_ID = 1312695472359735328  # Reemplaza con el ID de tu canal
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # Utilizar variable de entorno para el token

# Indicadores de estado
bot_ready = False
flask_ready = Event()  # Evento para señalar que Flask está listo
pending_webhooks = []  # Lista temporal para almacenar webhooks en espera


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint para manejar los webhooks de GitHub.
    """
    data = request.json

    # Esperar a que el bot esté listo y Flask se haya iniciado
    flask_ready.wait()

    # Agregar el webhook a la lista pendiente
    pending_webhooks.append(data)

    return jsonify({"status": "received"}), 200


async def process_webhook(data):
    """
    Procesa un webhook de GitHub y envía el mensaje al canal de Discord.
    """
    repo_name = data['repository']['name']
    action_type = data.get('action', 'Push')
    branch = data['ref'].split('/')[-1]

    for commit in data['commits']:
        author = commit['author']['name']
        timestamp = commit['timestamp']
        title = commit['message'].split("\n")[0]
        description = "\n".join(commit['message'].split("\n")[1:]) if len(commit['message'].split("\n")) > 1 else "*No se ha brindado una descripción*"
        commit_url = commit['url']

        await send_to_discord(repo_name, action_type, branch, author, timestamp, title, description, commit_url)


async def send_to_discord(repo_name, action_type, branch, author, timestamp, title, description, commit_url):
    """
    Enviar mensaje al canal de Discord.
    """
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


def run_flask():
    """
    Inicia el servidor Flask y señala que está listo.
    """
    flask_ready.set()  # Indicar que Flask está listo
    app.run(host="0.0.0.0", port=8080)


@bot.event
async def on_ready():
    """
    Evento que se ejecuta cuando el bot está listo.
    """
    global bot_ready
    bot_ready = True
    print(f"Bot conectado como {bot.user}")

    # Enviar mensaje de inicio al canal de Discord
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send(f"¡El bot {bot.user.name} se ha iniciado exitosamente!")

    # Procesar webhooks pendientes después del mensaje de inicio
    while pending_webhooks:
        webhook_data = pending_webhooks.pop(0)
        await process_webhook(webhook_data)


async def main():
    """
    Función principal para iniciar el bot y el servidor Flask.
    """
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    await bot.start(DISCORD_TOKEN)


# Ejecutar la función principal
asyncio.run(main())
