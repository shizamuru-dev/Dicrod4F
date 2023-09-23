import g4f
import json

import nextcord
from nextcord.ext import commands
from Config.cfg import settings

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!',intents=intents)


@bot.slash_command(name="clear", description="Clear message history")
async def clear_command(interaction: nextcord.Interaction):
    clear_json_channel(str(interaction.channel.id))
    await interaction.send("Message history cleared!")


@bot.slash_command(name="deepai", description="Changes provider to DeepAi")
async def deepai_command(interaction: nextcord.Interaction):
    change_json_provider(str(interaction.channel.id), g4f.Provider.DeepAi)
    await interaction.send("The provider has been successfully changed to: **DeepAI**")


@bot.slash_command(name="bing", description="Changes provider to Bing")
async def bing_command(interaction: nextcord.Interaction):
    change_json_provider(str(interaction.channel.id), g4f.Provider.Bing)
    await interaction.send("The provider has been successfully changed to: **Bing**")


@bot.slash_command(name="openassistant", description="Changes provider to OpenAssistant")
async def openassistant_command(interaction: nextcord.Interaction):
    change_json_provider(str(interaction.channel.id), g4f.Provider.OpenAssistant)
    await interaction.send("The provider has been successfully changed to: **OpenAssistant**")


@bot.slash_command(name="you", description="Changes provider to You")
async def you_command(interaction: nextcord.Interaction):
    change_json_provider(str(interaction.channel.id), g4f.Provider.You)
    await interaction.send("The provider has been successfully changed to: **You**")


@bot.slash_command(name="chatgptai", description="Changes provider to ChatgptAi")
async def chatgptAi_command(interaction: nextcord.Interaction):
    change_json_provider(str(interaction.channel.id), g4f.Provider.ChatgptAi)
    await interaction.send("The provider has been successfully changed to: **ChatgptAi**")


@bot.slash_command(name="usage", description="Instructions for using the bot")
async def usage_command(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="How to use this?",
                           description="Okay, to use this bot, just write the question you are interested in!\n\nAlso, for convenience, there are several commands, the list and description of which you can see below, or about entering / in the message panel...\n\n* **Usage** - Show... this message?\n* **Clear** - Clear message history\n* **Deepai** - Change provider to DeepAi | GPT 3.5 (Most stable)\n* **Bing** -  Change provider to Bing | GPT 4 (Default)\n* **Chatgptai** - Change provider to ChatgptAi | GPT 3.5\n* **You** - Change provider to You | GPT 3.5\n* **Openassistant** - Change provider to OpenAssistant | GPT 3.5",
                           color=nextcord.Color.dark_theme())
    embed.set_thumbnail("https://media.zenfs.com/en/thedailybeast.com/ad5b0dbb8d02c304c9a8652c07771b3e")
    embed.set_footer(text="Who is the provider? The provider is the site from which the ChatGPT is accessed")
    await interaction.channel.send(embed=embed)



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
                       "content": f"You can't write more than 2000 characters (in total), if you run into this threshold, put \"...\" (so that the total number of characters still does not exceed 2000) and when you are asked to add the remainder {promt}"}],
        )
        log = response[0:12]
        print(f"{provider.__name__}: {log}...")
        return response
    except Exception as e:
        print(f"{provider.__name__}:", e)
        return "**Error! Wait an hour or two, if it didn't help, write _shizamuru**"


def add_json_channel(channel_id: str, gpt: str, user: str):
    storage = open('Storage/data.json', 'r')
    data = json.load(storage)
    modify = data | {f"{channel_id}": {"dialog": f"promt:{user} answer:{gpt}", "cout": 0, "provider": "Bing"}}
    json_object = json.dumps(modify, indent=4)
    storage.close()
    with open("Storage/data.json", "w") as outfile:
        outfile.write(json_object)
        outfile.close()


def check_json_channel(channel_id: str):
    storage = open('Storage/data.json', 'r')
    data = json.load(storage)
    try:
        _ = data[channel_id]
        return True
    except:
        return False


def modify_json_channel(channel_id: str, gpt: str, user: str):
    storage = open('Storage/data.json', 'r')
    data = json.load(storage)
    if data[channel_id]['cout'] > 20:
        data[channel_id]['dialog'] = f" promt: {user} answer: {gpt}"
        data[channel_id]['cout'] = 0
    else:
        dialog_old = data[channel_id]['dialog']
        data[channel_id]['dialog'] = dialog_old + f" promt: {user} answer: {gpt}"
        cout_old = data[channel_id]['cout']
        data[channel_id]['cout'] = cout_old + 1
    modify = data

    json_object = json.dumps(modify, indent=4)
    storage.close()
    with open("Storage/data.json", "w") as outfile:
        outfile.write(json_object)
        outfile.close()


def get_json_channel(channel_id: str):
    storage = open('Storage/data.json', 'r')
    data = json.load(storage)
    return data[channel_id]['dialog']


def clear_json_channel(channel_id: str):
    storage = open('Storage/data.json', 'r')
    data = json.load(storage)
    data[channel_id]['cout'] = 0
    data[channel_id]['dialog'] = ""
    json_object = json.dumps(data, indent=4)
    storage.close()
    with open("Storage/data.json", "w") as outfile:
        outfile.write(json_object)
        outfile.close()


def change_json_provider(channel_id: str, provider: g4f.Provider.AsyncProvider):
    storage = open('Storage/data.json', 'r')
    data = json.load(storage)
    data[channel_id]['provider'] = provider.__name__
    modify = data

    json_object = json.dumps(modify, indent=4)
    storage.close()
    with open("Storage/data.json", "w") as outfile:
        outfile.write(json_object)
        outfile.close()


def get_json_provider(channel_id: str):
    storage = open('Storage/data.json', 'r')
    data = json.load(storage)
    return data[str(channel_id)]['provider']


@bot.event
async def on_ready():
    print(f"Bot started as {bot.user}")


@bot.event
async def on_message(message: nextcord.Message):
    if message.guild is not None:
        return
    else:
        if not check_json_channel(str(str(message.channel.id))):
            add_json_channel(str(message.channel.id), "", "")

        if message.content.startswith(settings["prefix"] + "clear"):
            clear_json_channel(str(message.channel.id))
            await message.channel.send("Message history cleared!")
        elif message.content.startswith(settings["prefix"] + "deepai"):
            change_json_provider(str(message.channel.id), g4f.Provider.DeepAi)
            await message.channel.send("The provider has been successfully changed to: **DeepAI**")
        elif message.content.startswith(settings["prefix"] + "bing"):
            change_json_provider(str(message.channel.id), g4f.Provider.Bing)
            await message.channel.send("The provider has been successfully changed to: **Bing**")
        elif message.content.startswith(settings["prefix"] + "openassistant"):
            change_json_provider(str(message.channel.id), g4f.Provider.OpenAssistant)
            await message.channel.send("The provider has been successfully changed to: **OpenAssistant**")
        elif message.content.startswith(settings["prefix"] + "you"):
            change_json_provider(str(message.channel.id), g4f.Provider.You)
            await message.channel.send("The provider has been successfully changed to: **You**")
        elif message.content.startswith(settings["prefix"] + "chatgptAi"):
            change_json_provider(str(message.channel.id), g4f.Provider.ChatgptAi)
            await message.channel.send("The provider has been successfully changed to: **ChatgptAi**")
        else:
            history = str(get_json_channel(str(message.channel.id)))

            if not message.content.startswith(settings["prefix"]) and message.author != bot.user:
                provider = get_provider(get_json_provider(str(message.channel.id)))
                answer = await run_provider(provider, history + str(message.content))
                modify_json_channel(str(message.channel.id), answer, message.content)
                await message.channel.send(answer)


bot.run(settings["token"])
