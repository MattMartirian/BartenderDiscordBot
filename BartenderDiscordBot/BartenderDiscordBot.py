from flask import Flask, request, jsonify
from threading import Thread
import asyncio
import discord_bot  # Importar las funciones desde discord_bot.py
import aiohttp

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
    asyncio.run(discord_bot.start_discord_bot())

if __name__ == "__main__":
    main()
