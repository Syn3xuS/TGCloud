import telebot, sqlite3
import random, sys, os
#TG Cloud by Syn3xuS
#python3.12.4 | telebot | sqlite3


def GenPass(len: int) -> str:
	"""Password length => password"""
	symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789~!@#$%^&*()_+-={}[]|:;<>,.?/"
	res = ""
	for _ in range(len):
		res += random.choice(symbols)
	return res


def Zip(object: str, filename: str = 'Archive.7z', password: str = '1234', command: str = '7z.exe', sizeonetom: str = '1024m'):
	"""Поверь что всё хорошо отработает, надо будет добавить дофига проверок сюда"""
	os.system(f'{command} a -v{sizeonetom} -p"{password}" "{filename}" "{object}" ')

def Unzip(filename: str, password: str = '1234', command: str = '7z.exe', output_directory: str = './') -> list[str] | int:
	"""Разархивирует архив (поддерживает многотомные архивы)"""
	os.system(f'{command} x -p"{password}" {filename} -o"{output_directory}"')


def CreateDB(filedb):
	with sqlite3.connect(filedb) as con:
		cur = con.cursor()
		cur.execute("""CREATE TABLE IF NOT EXISTS Settings (argument TEXT PRIMARY KEY, value TEXT)""")
		cur.execute("""CREATE TABLE IF NOT EXISTS Tokens (token TEXT PRIMARY KEY)""")
		cur.execute("""CREATE TABLE IF NOT EXISTS Docs (docname TEXT PRIMARY KEY, password TEXT)""")
		cur.execute("""CREATE TABLE IF NOT EXISTS Files (docname TEXT, filename TEXT, message_id TEXT PRIMARY KEY)""")
		cur.executemany("""INSERT OR IGNORE INTO Settings VALUES(?, ?)""", [
			('oblako_id', '0'),
			('7zipcommand', '7z.exe')
			])

def SetSettingDB(filedb, argument, value):
	with sqlite3.connect(filedb) as con:
		cur = con.cursor()
		cur.execute("""UPDATE Settings SET value = ? WHERE argument = ?""", (value, argument))

def GetSetting(filedb, argument):
	with sqlite3.connect(filedb) as con:
		cur = con.cursor()
		cur.execute(f"""SELECT value FROM Settings WHERE argument = ?""", (argument, ))
		res = cur.fetchone()
		return res[0] if res != None else None

def AddToken(filedb, token):
	with sqlite3.connect(filedb) as con:
		cur = con.cursor()
		cur.execute("""INSERT OR IGNORE INTO Tokens VALUES(?)""", (token,))

def DelToken(filedb, token):
	with sqlite3.connect(filedb) as con:
		cur = con.cursor()
		cur.execute(f"""DELETE FROM Tokens WHERE token = ?""", (token, ))

def GetTokens(filedb):
	with sqlite3.connect(filedb) as con:
		cur = con.cursor()
		cur.execute(f"""SELECT * FROM Tokens""")
		res = cur.fetchall()
		return res if res != None else None

def AddDoc(filedb:str, docname:str, password:str, files:list=None):
	"""files = [('name', 'id'), ('name', 'id'), ...]"""
	with sqlite3.connect(filedb) as con:
		cur = con.cursor()
		cur.execute(f"""INSERT OR IGNORE INTO Docs VALUES(?, ?)""", (docname, password))
		cur.executemany(f"""INSERT OR IGNORE INTO Files VALUES('{docname}', ?, ?)""", files)

def DelDoc(filedb:str, docname:str):
	with sqlite3.connect(filedb) as con:
		cur = con.cursor()
		cur.execute(f"""DELETE from Docs WHERE docname = ?""", (docname, ))
		cur.execute(f"""DELETE from Files WHERE docname = ?""", (docname, ))

def GetDocs(filedb:str):
	with sqlite3.connect(filedb) as con:
		cur = con.cursor()
		cur.execute(f"""SELECT docname FROM Docs""")
		res = cur.fetchall()
		return res if res != None else None

def GetFiles(filedb:str, docname:str):
	with sqlite3.connect(filedb) as con:
		cur = con.cursor()
		cur.execute(f"""SELECT * FROM Files WHERE docname = '{docname}'""")
		res = cur.fetchall()
		return res if res != None else None

def SearchDocInDB(filedb: str, docname: str):
	with sqlite3.connect(filedb) as con:
		cur = con.cursor()
		cur.execute(f"""SELECT * FROM Docs WHERE docname = ?""", (docname, ))
		res = cur.fetchone()
		return res if res != None else None


def SendFile(token: str, chat_id: str | int, file: str, mode: str = 'path') -> str | int:
	"""token + chat id + file + mode (path or id) => message id or Error(0)"""
	bot = telebot.TeleBot(token)
	match mode:
		case 'id':
			bot.send_document(chat_id, file)
			return file
		case 'path':
			with open(file, 'rb') as f:
				msg = bot.send_document(chat_id, f)
				return msg.message_id
	return 0

def LoadFile(token: str, chat_id: str, message_id: str, filename: str):
	"""token + file id + file(path)=> Error(0) or Good(1)"""
	bot = telebot.TeleBot(token)
	msg = bot.forward_message(chat_id, chat_id, message_id)
	file = bot.get_file(msg.document.file_id)
	try: download_file = bot.download_file(file.file_path)
	except: pass
	bot.delete_message(chat_id, msg.message_id)
	with open(filename, 'wb') as f: f.write(download_file)

def SendMessage(token: str, chat_id: str | int) -> str | int:
	"""token + chat id + file + mode (path or id) => file id or Error(0)"""
	bot = telebot.TeleBot(token)
	bot.send_message(chat_id, 'HELLO')
	a = bot.forward_message(chat_id, chat_id, 6)
	print(a)
	print(a.document.file_id)
	SendFile(token, chat_id, a.document.file_id, 'id')
	bot.delete_message(chat_id, a.message_id)
	return 0



def _newDB(args):
	if(len(args)>=3):
		CreateDB(args[2])
def _setDB(args):
	if(not len(args)>=5): return print("Мало аргументов")
	if(not os.path.exists(args[2])): return print("Конфиг не найден!")
	SetSettingDB(args[2], args[3], args[4])
def _addTOKEN(args):
	if(not len(args)>=4): return print("Мало аргументов")
	if(not os.path.exists(args[2])): return print("Конфиг не найден!")
	AddToken(args[2], args[3])
def _delTOKEN(args):
	if(not len(args)>=4): return print("Мало аргументов")
	if(not os.path.exists(args[2])): return print("Конфиг не найден!")
	DelToken(args[2], args[3])

def _info(args): pass

def _list(args):
	if(not len(args)>=3): return print("Мало аргументов")
	if(not os.path.exists(args[2])): return print("Конфиг не найден!")
	docs = GetDocs(args[2])
	print("СПИСОК АРХИВОВ И ЕГО ЧАСТЕЙ:")
	if(docs==[]): print('ПУСТО')
	for doc in docs:
		file = GetFiles(args[2], doc[0])
		print(f'{doc[0]} ({int(file[-1][1].split('.')[-1])})')

def _send(args):
	print('Отправка файлов')
	if(not len(args)>=5): return print("Мало аргументов")
	if(not os.path.exists(args[2])): return print("Конфиг не найден!")
	if(not os.path.exists(args[3])): return print("Директория/файл не существует или неверно указан путь!")
	if(not SearchDocInDB(args[2], args[4]) == None): return print("Архив под таким именем уже есть!")
	if(GetTokens(args[2]) == []): return print("Токенов нет")
	db = args[2]
	path = args[3]
	docname = args[4]
	password = GenPass(1024)
	oblako_id = GetSetting(db, 'oblako_id')
	tokens = GetTokens(db)
	for x in os.listdir('./'):
		if docname in x:
			print(f"УДАЛЯЮ {x}")
			os.remove(x)
	Zip(path, docname, password, sizeonetom='10m')
	files = [ x for x in os.listdir('./') if docname in x]
	print(files)
	ids = []
	print(oblako_id)
	for file in files:
		res = 1
		while(res):
			for token in tokens:
				try:
					id = SendFile(token[0],  oblako_id  , f'{file}')
					print(f'Отправлен {file}')
					ids.append((file, id))
					os.remove(file)
					res = 0
					break
				except BaseException as e:
					print(f'Неполучилось отправить {file}')
					print(f'ОШИБКА: {e}')
					continue
	AddDoc(db, docname, password, ids)

def _load(args):
	print('Загрузка файлов')
	if(not len(args)>=4): return print("Мало аргументов")
	if(not os.path.exists(args[2])): return print("Конфиг не найден!")
	doc = SearchDocInDB(args[2], args[3])
	if(doc==None): return print("Такого архива нет!")
	tokens = GetTokens(args[2])
	if(tokens == []): return print("Токенов нет")
	password = doc[1]
	files = GetFiles(args[2], args[3])
	oblako_id = GetSetting(args[2], 'oblako_id')
	for file in files:
		res = 1
		while(res):
			for token in tokens:
				try:
					LoadFile(token[0], oblako_id, file[2], f'{file[1]}')
					print(f'{file[1]} успешно скачен')
					res = 0
					break
				except BaseException as e:
					print(f'Невышло скачать {file[1]}')
					print(f'ОШИБКА: {e}')
					continue
	Unzip(files[0][1], password, output_directory=f'./{args[3].split('.')[0]}')
	for file in files: os.remove(file[1])

def _delete(args):
	if(not len(args)>=4): return print("Мало аргументов")
	if(not os.path.exists(args[2])): return print("Конфиг не найден!")
	doc = SearchDocInDB(args[2], args[3])
	if(doc==None): return print("Архив не найден")
	DelDoc(args[2], args[3])
	print(f'{args[3]} удалён из {args[2]}')

def _help(args):
	print("Потом")

def main():
	args = sys.argv
	if(len(args)<=1): return print("Слишком мало аргументов")
	#print(args)
	match args[1]:
		case '-newDB': _newDB(args)
		case '-setDB': _setDB(args)
		case '-addTOKEN': _addTOKEN(args)
		case '-delTOKEN': _delTOKEN(args)
		case '_info': _info(args)
		case '-list': _list(args)
		case '-send': _send(args)
		case '-load': _load(args)
		case '-delete': _delete(args)

		case '-test':
			#SendFile(GetTokens('one.db')[0][0], '-1002161968272', '7z.exe')
			SendMessage(GetTokens('one.db')[1][0], '-1002161968272')
			pass
#=================================#
		case '-h' | '-help': _help(args)
		case _: print('Такого аргумента нет')


if '__main__' == __name__: main()