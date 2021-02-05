import json,requests,os,discord,math
from dotenv import load_dotenv
from discord.ext import commands,tasks

def convertir_horas(relative: int):
	relative *= -1
	#horario = [math.ceil(relative/3600),int((relative/60))%60,relative%60]
	return math.ceil(relative/3600)

class competencia():
	def __init__(self,dicc):
		self.nombre = dicc['name']
		self.tipo = dicc['type']
		self.faltan = convertir_horas(dicc['relativeTimeSeconds'])
		try:
			self.url = dicc['websiteUrl']
		except KeyError:
			self.url = ""

def solve(b: bool):
	respuesta = requests.get("https://codeforces.com/api/contest.list?lang=en")
	nuevo = False
	l = []
	try:
		f = open("competencias.txt","r+",encoding="utf-8")
		l = f.readline()[:-1].split('~')
	except FileNotFoundError:
		f = open("competencias.txt","w+",encoding="utf-8")

	compes = []
	compes_nuevas = []
	for i in respuesta.json()["result"]:
		if i['phase']=='BEFORE':
			if i['name'] in l:
				compes.append(f"{i['type']}: {i['name']} en {convertir_horas(i['relativeTimeSeconds'])} horas")
			else:
				compes_nuevas.append(f"NUEVA {i['type']}!: {i['name']} en {convertir_horas(i['relativeTimeSeconds'])} horas")
				f.write(i['name']+"~")
				nuevo = True
	f.close()
	if b:
		return '```autohotkey\n'+'\n'.join(compes_nuevas[::-1])+'\n```',nuevo
	else:
		return '```autohotkey\n'+'\n'.join(compes_nuevas[::-1]+compes[::-1])+'\n```'

@tasks.loop(hours=8)
async def chequear_compes():
	imprimir, new = solve(1)
	if new:
		guild = discord.utils.get(bot.guilds,name=GUILD)
		canal = discord.utils.get(guild.text_channels,name="competencias")
		await canal.send(imprimir)

#Cosas de bots
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


intents = discord.Intents.default()
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='!',intents=intents)

@bot.event
async def on_ready():
	chequear_compes.start()

@bot.command(name="contest",help="Muestra las competencias actualmente disponibles en CF")
async def contest(ctx):
	imprimir = solve(0)
	await ctx.send(imprimir)

bot.run(TOKEN)
