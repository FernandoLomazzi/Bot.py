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
	def __eq__(self,other):
		return self.nombre==other

def solve():
	respuesta = requests.get("https://codeforces.com/api/contest.list")
	mensaje = ""
	nuevo = False
	l = []
	try:
		f = open("competencias.txt","r+",encoding="utf-8")
		l = f.readline().split('-')[:-1]
	except FileNotFoundError:
		f = open("competencias.txt","w+",encoding="utf-8")

	for i in respuesta.json()["result"]:
		if i['name'] in l:
			mensaje = f"{i['name']} en {convertir_horas(i['relativeTimeSeconds'])} horas\n"+mensaje
		elif i['phase']=="BEFORE":
			mensaje = f"NUEVA!: {i['name']} en {convertir_horas(i['relativeTimeSeconds'])} horas\n"+mensaje
			f.write(i['name']+"-")
			nuevo = True
	f.close()
	return "```autohotkey\n"+mensaje+'```',nuevo

@tasks.loop(hours=8)
async def chequear_compes():
	imprimir, new = solve()
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
	#print("ok")
	chequear_compes.start()

@bot.command(name="contest",help="Muestra las competencias actualmente disponibles en CF")
async def contest(ctx):
	imprimir = solve()[0]
	await ctx.send(imprimir)

bot.run(TOKEN)