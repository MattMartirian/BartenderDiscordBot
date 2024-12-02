import discord
from discord.ext import commands
import asyncio
import os

# Configuración del bot
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_CHANNEL_ID = 1312695472359735328  # Reemplaza con el ID de tu canal
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

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
