import discord
import json
import copy
import random
import time
from discord.commands.options import Option
from discord.ext import commands
from discord.ui import InputText, Modal
from discord.ui.select import Select

bot = commands.Bot(command_prefix="!")
db={}

def loaddb():
    global db
    with open(r"D:\anaconda3\envs\py39\codes\sulmun\db.json", mode="r", encoding="utf-8") as f:
        db=json.load(f)

def writedb(dbc):
    global db
    db=copy.deepcopy(dbc)
    with open(r"D:\anaconda3\envs\py39\codes\sulmun\db.json", mode="w", encoding="utf-8") as f:
        json.dump(copy.deepcopy(dbc), f, indent=2, ensure_ascii=False)

def ensuredb(ctx, _id, title):
    global db
    try:
        db[str(ctx.guild.id)]
        try:
            db[str(ctx.guild.id)][str(ctx.channel.id)]
            try:
                db[str(ctx.guild.id)][str(ctx.channel.id)][_id]
                try:
                    db[str(ctx.guild.id)][str(ctx.channel.id)][_id]["title"]
                    writedb(db)
                    return
                except KeyError:
                    db[str(ctx.guild.id)][str(ctx.channel.id)][_id]={"title": title, "datas":[]}
            except KeyError:
                db[str(ctx.guild.id)][str(ctx.channel.id)][_id]={}
        except KeyError:
            db[str(ctx.guild.id)][str(ctx.channel.id)]={}
    except KeyError:
        db[str(ctx.guild.id)]={}
    ensuredb(ctx, _id, title)

def getguildpolls(ctx):
    global db
    loaddb()
    result=[]
    for key, value in db[str(ctx.guild.id)][str(ctx.channel.id)].items():
        result.append(discord.SelectOption(label=str(value["title"]), value=str(key)))

class MyModal(Modal):
    def __init__(self, title, _id=str(time.time()).split(".")[1]+str(random.randint(0, 9))+str(random.randint(0, 9))) -> None:
        super().__init__(title=title)
        self.value={}
        self.custom_id=_id
        self.add_item(InputText(label="asdf", placeholder="asdff"))

    async def callback(self, interaction):
        for child in self.children:
            self.value[child.label]=child.value

        ensuredb(interaction, self.custom_id, self.title)
        db[str(interaction.guild_id)][str(interaction.channel_id)][str(self.custom_id)]["datas"].append(self.value)
        writedb(db)
        await interaction.response.send_message("설문 내용이 저장되었습니다! 감사합니다!", ephemeral=True)

class SelectPolls(Select):
    def __init__(self, ctx):
        super().__init__(min_values=1, max_values=1, options=getguildpolls(ctx))

    async def callback(self, interaction: discord.Interaction):
        # do nothing
        #just like my life
        return

@bot.event
async def on_ready():
    print("ready")
    loaddb()

@bot.slash_command(guild_ids=[820964115131793449, 851650387039617035, 803249696638238750])
async def 설문조사(ctx: discord.ApplicationContext, option: Option(str, "설문조사로 뭘 하실 건가요?", choices=["작성"])):#, "조회"])):
    if option == "작성":
        #await ctx.defer()
        await ctx.send_modal(MyModal(title="asdf", _id="447632695"))
    elif option == "조회":
        view=SelectPolls(ctx)
        await ctx.respond("어떤 설문조사죠? 아이디로 알려주세요!", view=view, ephemeral=True)
        await view.wait()
        await ctx.respond(f"아, `{view.values[0]}`요? 잠시만요...", ephemeral=True)

bot.run()