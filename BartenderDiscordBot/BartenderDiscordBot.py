from flask import Flask, request, jsonify
import asyncio
from threading import Thread
import discord_bot  # Asegúrate de que este módulo contiene tus funciones de Discord, como send_to_discord

# Crear la aplicación Flask
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
            discord_bot.send_to_discord(repo_name, action_type, branch, author, timestamp, title, description, commit_url),
            discord_bot.bot.loop
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

    # Iniciar el bot de Discord en un hilo separado
    discord_thread = Thread(target=start_discord_bot)
    discord_thread.start()

if __name__ == "__main__":
    main()
