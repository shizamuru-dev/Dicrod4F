import g4f
import json
import discord

from Config.cfg import settings

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)


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
            messages=[{"role": "user", "content": f"You can't write more than 2000 characters (in total), if you run into this threshold, put "..." (so that the total number of characters still does not exceed 2000) and when you are asked to add the remainder {promt}"}],
        )
        log = response[0:12]
        print(f"{provider.__name__}: {log}...")
        return response
    except Exception as e:
        print(f"{provider.__name__}:", e)
        return "**Mistake! Wait an hour or two, if it didn't help, write _shizamuru**"


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
async def on_message(message: discord.Message):
    if message.guild is not None:
        return
    else:
        if not check_json_channel(str(str(message.channel.id))):
            add_json_channel(str(message.channel.id), "", "")

        if message.content.startswith(settings["prefix"] + "clear"):
            clear_json_channel(str(message.channel.id))
            await message.channel.send("The history of successful messages has been cleared!")
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
        elif message.content.startswith(settings["prefix"] + "chatgptai"):
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
