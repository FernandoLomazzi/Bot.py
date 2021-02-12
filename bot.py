import json,requests,os,discord,math
from dotenv import load_dotenv
from discord.ext import commands,tasks

def convertir_horas(relative: int):
	relative *= -1
	#horario = [math.ceil(relative/3600),int((relative/60))%60,relative%60]
	return math.ceil(relative/3600)

def consultar_API():
	respuesta = requests.get("https://codeforces.com/api/contest.list?lang=en")
	return respuesta.json()['result']

def solve(b: bool):
	nuevo = False
	try:
		f = open("competencias.txt","r+",encoding="utf-8")
		comp = [x.strip() for x in f.readlines()]
	except FileNotFoundError:
		f = open("competencias.txt","w+",encoding="utf-8")
		comp = []
	texto = ""
	if b:
		for i in consultar_API():
			tiempo = convertir_horas(i['relativeTimeSeconds'])
			if 0<=tiempo<=36 and i['name'] not in comp:
				nuevo = True
				texto = f"Mañana {i['type']}!: {i['name']} en {tiempo} horas\n"+texto
				f.write(i['name'])
				f.write('\n')
		f.close()
		return '```autohotkey\n'+texto+'```',nuevo
	else:
		for i in consultar_API():
			if i['phase'] == 'BEFORE':
				texto = f"{i['type']}: {i['name']} en {convertir_horas(i['relativeTimeSeconds'])} horas\n"+texto
			else:
				break
		f.close()
		return '```autohotkey\n'+texto+'```'		

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
