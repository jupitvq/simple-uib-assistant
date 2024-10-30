import logging
import os
from discord.ext import commands
from discord import app_commands
import discord
import pickle
import numpy as np
import string
from util.parser import JSONParser
from dotenv import load_dotenv

def preprocess(chat):
    chat = chat.lower()
    tandabaca = tuple(string.punctuation)
    chat = ''.join(ch for ch in chat if ch not in tandabaca)
    return chat

def bot_response(chat, pipeline, jp):
    chat = preprocess(chat)
    res = pipeline.predict_proba([chat])
    max_prob = max(res[0])
    if max_prob < 0.2:
        return "Maaf, saya tidak mengerti, jika anda butuh bantuan harap menghubungi humas kami.", None
    else:
        max_id = np.argmax(res[0])
        pred_tag = pipeline.classes_[max_id]
        return jp.get_response(pred_tag), pred_tag

with open("model_chatbot.pkl", "rb") as model_file:
    pipeline = pickle.load(model_file)

jp = JSONParser()
jp.parse("data/intents.json")

guild_id = os.getenv("MY_GUILD_ID")
if not guild_id:
    raise ValueError("Tidak ada ID guild yang ditemukan di environment variable MY_GUILD_ID")

MY_GUILD = discord.Object(id=int(guild_id))

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync()

intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    await client.setup_hook()
    print('------')

@client.tree.command()
@app_commands.rename(pertanyaan='pertanyaan')
@app_commands.describe(pertanyaan='apa yang mau ditanya ke AI')
async def tanya(interaction: discord.Interaction, pertanyaan: str):
    
    await interaction.response.defer()
    response, tag = bot_response(pertanyaan, pipeline, jp)
    await interaction.followup.send(f"\n{response}")


def main():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("Tidak ada token bot discord yang ditemukan di environment variable DISCORD_BOT_TOKEN")

    client.run(token)

if __name__ == '__main__':
    main()