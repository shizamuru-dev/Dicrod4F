import os
import sys
import g4f
import sqlite3
import pathlib
import logging
import nextcord

from pathlib import Path
from Config.cfg import settings
from nextcord.ext import commands
from logging import StreamHandler, Formatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

if not pathlib.Path("./Storage").is_dir():
    logger.info("Create \"Storage\" directory")
    os.mkdir("./Storage")

base = sqlite3.connect('./Storage/base.db')
cursor = base.cursor()

logger.info("Database connected!")


def check_table():
    try:
        check = cursor.execute('''select * from Users;''')
    except Exception as e:
        if e.args[0] == "no such table: Users":
            cursor.execute('''create table Users(id TEXT,dialogue TEXT,provider TEXT, cout INTEGER);''')
            logger.info("Table created...")
            base.commit()


check_table()


def create_row(channel_id: str):
    cursor.execute(f'INSERT INTO Users (id,dialogue,provider,cout) VALUES ("{channel_id}","","Bing",0)')
    base.commit()
    logger.info(f"Created row for {channel_id}")


def check_row(channel_id: str):
    try:
        result = cursor.execute(f'Select provider from Users where id = {channel_id}')
        t = result.fetchall()[0][0]
        logger.info(t)
        return True
    except:
        return False


def modify_row(channel_id: str, gpt: str, user: str):
    cout_fetch = cursor.execute(f'Select cout from Users where id = {channel_id}')
    cout = cout_fetch.fetchall()[0][0]

    if cout > 20:
        cursor.execute(f"UPDATE Users set dialogue = '' where id = '{channel_id}'")
        cursor.execute(f"UPDATE Users set cout = 0 where id = '{channel_id}'")
        base.commit()
    else:
        history_old_fetch = cursor.execute(f"select dialogue from Users where id = '{channel_id}'")
        history_new = history_old_fetch.fetchall()[0][0] + f" promt: {user} answer: {gpt}"
        cursor.execute(f"UPDATE Users set dialogue = '{history_new}' where id = '{channel_id}'")
        cursor.execute(f"UPDATE Users set cout = {cout + 1} where id = {channel_id}")
        base.commit()


def get_row_history(channel_id: str):
    history_fetch = cursor.execute(f'Select dialogue from Users where id = {channel_id}')
    history = history_fetch.fetchall()[0][0]
    return history


def clear_row_history(channel_id: str):
    cursor.execute(f"UPDATE Users set dialogue = '' where id = '{channel_id}'")
    cursor.execute(f"UPDATE Users set cout = 0 where id = {channel_id}")
    base.commit()


def change_row_provider(channel_id: str, provider: g4f.Provider.AsyncProvider):
    cursor.execute(f"UPDATE Users set provider = '{provider.__name__}' where id = '{channel_id}'")
    base.commit()


def get_row_provider(channel_id: str):
    provider_fetch = cursor.execute(f'Select provider from Users where id = {channel_id}')
    provider = provider_fetch.fetchall()[0][0]
    return provider


def get_provider(name: str):
    if name == "DeepAi":
        return g4f.Provider.DeepAi
    elif name == "Bing":
        return g4f.Provider.Bing
    elif name == "OpenAssistant":
        return g4f.Provider.OpenAssistant
    elif name == "You":
        return g4f.Provider.You
    elif name == "ChatgptAi":
        return g4f.Provider.ChatgptAi


async def run_provider(provider: g4f.Provider.AsyncProvider, promt: str):
    try:
        response = await provider.create_async(
            model=g4f.models.default.name,
            messages=[{"role": "user",
                       "content": f"You can't write more than 2000 characters (in total) if you"
                                  f"run into this threshold, put \"...\" (so that the total number of characters "
                                  f"still did not exceed 2000 ) and when you are asked to add the rest {promt}"}],
        )
        log = response[0:12]
        logger.info(f"{provider.__name__}: {log}...")
        return response
    except Exception as e:
        logger.error(f"{provider.__name__}:", e)
        return "**Error! Wait an hour or two, if it didn't help, write _shizamuru**"


@bot.event
async def on_message(message: nextcord.Message):
    id = str(message.channel.id)

    if message.guild is not None:
        return
    else:
        if not check_row(id):
            logger.info(f'Create row from {id}')
            create_row(id)

        if message.content.startswith(settings["prefix"] + "clear"):
            clear_row_history(id)
            await message.channel.send("Message history has been successfully cleared!")
        elif message.content.startswith(settings["prefix"] + "deepai"):
            change_row_provider(id, g4f.Provider.DeepAi)
            await message.channel.send("The provider has been successfully changed to: **DeepAI**")
        elif message.content.startswith(settings["prefix"] + "bing"):
            change_row_provider(id, g4f.Provider.Bing)
            await message.channel.send("The provider has been successfully changed to: **Bing**")
        elif message.content.startswith(settings["prefix"] + "openassistant"):
            change_row_provider(id, g4f.Provider.OpenAssistant)
            await message.channel.send("The provider has been successfully changed to: **OpenAssistant**")
        elif message.content.startswith(settings["prefix"] + "you"):
            change_row_provider(id, g4f.Provider.You)
            await message.channel.send("The provider has been successfully changed to: **You**")
        elif message.content.startswith(settings["prefix"] + "chatgptAi"):
            change_row_provider(id, g4f.Provider.ChatgptAi)
            await message.channel.send("Провайдер успешно изменён на: **ChatgptAi**")
        else:
            history = get_row_history(id)

            if not message.content.startswith(settings["prefix"]) and message.author != bot.user:
                provider = get_provider(get_row_provider(id))
                answer = await run_provider(provider, history + str(message.content))
                modify_row(id, answer, message.content)
                await (message.channel.send(answer))


@bot.slash_command(name="clear", description="Clear message history")
async def clear_command(interaction: nextcord.Interaction):
    clear_row_history(str(interaction.channel.id))
    await interaction.send("Message history has been successfully cleared!")


@bot.slash_command(name="deepai", description="Changes provider to DeepAi")
async def deepai_command(interaction: nextcord.Interaction):
    change_row_provider(str(interaction.channel.id), g4f.Provider.DeepAi)
    await interaction.send("The provider has been successfully changed to: **DeepAI**")


@bot.slash_command(name="bing", description="Changes provider to Bing")
async def bing_command(interaction: nextcord.Interaction):
    change_row_provider(str(interaction.channel.id), g4f.Provider.Bing)
    await interaction.send("The provider has been successfully changed to: **Bing**")


@bot.slash_command(name="openassistant", description="Changes provider to OpenAssistant")
async def openassistant_command(interaction: nextcord.Interaction):
    change_row_provider(str(interaction.channel.id), g4f.Provider.OpenAssistant)
    await interaction.send("The provider has been successfully changed to: **OpenAssistant**")


@bot.slash_command(name="you", description="Changes provider to You")
async def you_command(interaction: nextcord.Interaction):
    change_row_provider(str(interaction.channel.id), g4f.Provider.You)
    await interaction.send("The provider has been successfully changed to: **You**")


@bot.slash_command(name="chatgptai", description="Changes provider to ChatgptAi")
async def chatgptAi_command(interaction: nextcord.Interaction):
    change_row_provider(str(interaction.channel.id), g4f.Provider.ChatgptAi)
    await interaction.send("The provider has been successfully changed to: **ChatgptAi**")


@bot.slash_command(name="usage", description="Instructions for using the bot")
async def usage_command(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="How to use this?",
                           description="So, to use this bot, just write the question you are interested in "
                                       "\n\Also, for convenience, there are several commands, a list and a description "
                                       "which you can see below / in the message panel...\n\n* **Usage** - "
                                       "Show... is this a message?\n* **Clear** - Cleare message history\n* "
                                       "**Deepai** - Change provider to DeepAi | GPT 3.5 \n* "
                                       "**Bing** -  Change provider to Bing | GPT 4 (Default)\n* "
                                       "**Chatgptai** - Change provider to ChatgptAi | GPT 3.5 (Most Stable)\n* **You** - "
                                       "Change provider to You | GPT 3.5\n* **Openassistant** - Change "
                                       "provider to OpenAssistant | GPT 3.5",
                           color=nextcord.Color.dark_theme())
    embed.set_thumbnail("https://media.zenfs.com/en/thedailybeast.com/ad5b0dbb8d02c304c9a8652c07771b3e")
    embed.set_footer(text="What kind of providers? The provider is the site through which the ChatGPT is accessed ")
    await interaction.channel.send(embed=embed)


@bot.event
async def on_ready():
    logger.info(f"Bot started as {bot.user}")


bot.run(settings["token"])
