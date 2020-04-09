import discord
import re
import time
import tzlocal
from datetime import datetime as dt
from os import walk

class MaxSizeList(object):
    def __init__(self, max_length):
        self.max_length = max_length
        self.ls = []

    def push(self, st):
        if len(self.ls) == self.max_length:
            self.ls.pop(0)
        self.ls.append(st)

    def get_list(self):
        return self.ls

bot_token = "Njk3NTI2ODU3NDIzMTI2NjQ4.Xo4rxg.jkUOf2EwmfO9fmRPWfsZ8qOjpxo"

prefix = "$"

last = ""
played = []
history = MaxSizeList(50)
gravando = False

client = discord.Client()

# formato:
# Now playing __**[Fu Manchu - The Action is Go (1997) - Full Album](https://www.youtube.com/watch?v=EG6F1m1Gi4k)**__ requested by <@213803236044439553>.
def extract_links(s):
    l = []
    for x in re.findall(r"\]\((.+)\)", s):
        l.append(x)
    return l


def exctract_names(s):
    l = []
    for x in re.findall(r"\*\[(.+)\]\(", s):
        l.append(x)
    return l


def write_playlist(arr):
    nome = "playlists/" + str(str(int(time.time())) + ".txt")
    f = open(nome, "w")

    for x in arr:
        s = x[0] + ", " + x[1]
        f.write(s)
        f.write("\n")

    f.close()


def listar_playlists():
    s = ""
    ids = []
    local_tz = tzlocal.get_localzone()
    (_, _, fns) = next(walk("playlists/"))
    for x, fn in enumerate(fns[:10]):
        ts = float(fn.replace(".txt", ""))
        data = dt.fromtimestamp(ts, local_tz).strftime("%d/%m/%Y %H:%M")
        s += str(x+1) + " | salva às: " + str(data) + "\n"
        ids.append(fn)

    return (s, ids)


def get_playlist(q):
    ls = listar_playlists()[1][q-1]

    f = open("playlists/" + str(ls), "r")
    return f


def ultima_playlist():
    ul = 0
    (_, _, fns) = next(walk("playlists/"))
    for fn in fns:
        ns = fn.replace(".txt", "")
        dt = int(ns)
        if dt > ul:
            ul = dt

    f = open("playlists/" + str(ul) + ".txt", "r")
    return f


@client.event
async def on_ready():
    print(f'Conectado! {client.guilds}')


@client.event
async def on_message(m):
    global last, played, gravando, history

    if type(m.channel) is discord.DMChannel:
        link = m.content
        for c in client.guilds[0].channels:
            if c.name == "radio":
                conteudo = "" + link
                await c.send(content = conteudo)

    if m.content.startswith(prefix + "playlist ultima"):
        f = discord.File(ultima_playlist())
        await m.channel.send(content = "Segue a ultima playlist gravada aì" , file = f)

    if m.content.startswith(prefix + "playlist listar"):
        s = "Playlists Salvas: \n"
        s += listar_playlists()[0]
        s += "Envie ```" + prefix + "playlist baixar <nmr> ``` para baixar a playlist" 
        await m.channel.send(content = s)

    if m.content.startswith(prefix + "playlist baixar "):
        qr = int(m.content.replace(prefix + "playlist baixar ", ""))
        pl = discord.File(get_playlist(qr))
        await m.channel.send(content = "Segura essa merda ai bixo:", file = pl)

    if str(m.channel) == "radio":
        if len(m.embeds) > 0 and str(m.embeds[0].description).startswith("`1`"):
            last = m.embeds[0].description
       
        if len(m.embeds) > 0 and str(m.embeds[0].description).startswith("Now playing __"):
            links = extract_links(str(m.embeds[0].description))
            names = exctract_names(str(m.embeds[0].description))
            comb = list(zip(names, links))[0]
            history.push(comb)

        if m.content.startswith(prefix + "historico save "):
            await m.channel.send(content = "Salvando esse inferno")
            qr = int(m.content.replace(prefix + "historico save ", "")) * -1
            saved = history.get_list()[qr:]
            write_playlist(saved)
            await m.channel.send(content = "Ultimas " + str(qr * -1) + " músicas tocadas salvas em uma playlist")
        
        if len(m.embeds) > 0 and str(m.embeds[0].description).startswith("Now playing __") and gravando == True:
            links = extract_links(str(m.embeds[0].description))
            names = exctract_names(str(m.embeds[0].description))
            comb = list(zip(names, links))[0]
            played.append(comb)

        if m.content.startswith(prefix + "queue save"):
            links = extract_links(last)
            write_playlist(links)
            await m.channel.send(content = "Tá comigo ta com Deus!\nQueue atual gravada!")

        if m.content.startswith(prefix + "gravar"):
            if gravando == False:
                gravando = True
                await m.channel.send(content = "Tá comigo ta com Deus! \nGravando musicas tocadas!")
            elif gravando == True:
                await m.channel.send(content = "Já ta gravando caralho!!")
            
        if m.content.startswith(prefix + "salvar"):
            if gravando == True:
                if len(played) > 0:
                    write_playlist(played)
                    played = []
                    gravando = False
                    await m.channel.send(content = "Tocadas gravadas!")
                else:
                    await m.channel.send(content = "Nenhuma música foi tocada ate agora!")
            else: 
                await m.channel.send(content = "Eu não to gravando ainda buceta")

        if "Death Grips" in m.content:
            await m.channel.send(content = "Vai tomar no cu Leumas")

client.run(bot_token)
