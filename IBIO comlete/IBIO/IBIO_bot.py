import discord
from discord.ext import commands
import datetime
from discord.utils import get
import youtube_dl
import os
from random import choice

commander = '*'
TOKEN = ""
ibio = commands.Bot(command_prefix=commander)
const_month = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
               'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
t_f = False
s_f = False
stopped = list()


@ibio.event
async def on():
    print('Запуск')


@ibio.command()
async def ready(ctx):  # Задаются базовые значения для включения муз. возможностей бота
    global t_f, s_f
    await ctx.message.channel.send('```IBIO``` подключён.')
    await ctx.message.author.voice.channel.connect(reconnect=True)
    t_f = True
    s_f = True


@ibio.command()
async def IBIO_help(ctx):  # Вывод основных комманд бота
    location = (os.getcwd()[0:-5]) + r'\сайт\url\now_url.txt'  # переход к файлу с сылкой, созданной ngrok
    file = open(location, mode='rt')
    url = file.read()
    await ctx.message.channel.send('```IBIO команды:\n'
                                   'ready - вкл/выкл бот\n'
                                   'clarify "исчесление времени" - говорит время\n'
                                   'play "ссылка на видео с ютуба" - проигрывает музыку\n'
                                   'rem "Любые символы" - запоминает вашу фразу\n'
                                   'tell - воспроизводит ваши воспоминания\n'
                                   '\n'
                                   '\n'
                                   f'Все комманды находятся на нашем сайте``` {url}')


@ibio.command()
async def clarify(ctx, args):  # Самое бесполезное, но нужная именно мне функция, показ даты и времени
    arg = (''.join((''.join(args.split('('))).split(')'))).lower()
    day = int((str((datetime.datetime.now().date())).split('-'))[2])
    month = const_month[int((str((datetime.datetime.now().date())).split('-'))[1])]
    year = int((str((datetime.datetime.now().date())).split('-'))[0])
    if arg == 'дата':
        await ctx.message.channel.send(f'```{day} {month} {year} год.```')
    elif arg == 'время':
        await ctx.message.channel.send(f'```{datetime.datetime.now().hour}:{datetime.datetime.now().minute}```')


def on_off(ctx):  # вспомогательная функция для основной play, нужна для создания о запуска очереди
    # почти все функции повторяются из основной.
    global t_f, stopped, voice
    t_f = True
    song_there = os.path.isfile('song.mp3')
    try:
        if song_there:
            os.remove('song.mp3')
    except PermissionError:
        pass
    print('Закон.')
    stopped.remove(stopped[0])
    if len(stopped) != 0:
        try:
            t_f = False
            url = stopped[0]
            voice = get(ibio.voice_clients, guild=ctx.guild)
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }],
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            for file in os.listdir('./'):
                if file.endswith('.mp3'):
                    os.rename(file, 'song.mp3')
            voice.play(discord.FFmpegPCMAudio('song.mp3'), after=lambda e: on_off(ctx))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 1
        except Exception:
            on_off(ctx)


@ibio.command()
async def play(ctx, url='False'):  # Гдавная функция для проигрывания музыки.
    global t_f, voice, stopped
    if s_f:  # пока не запущена *ready мы не можем работать с очередью
        if url != 'music':  # если пользователь просит музыку, мы её запускаем, а не добавляем в очердь
            stopped.append(url)  # если пользователь кинул ссылку на музыку она добавляется в очередь
        print(stopped)
        url = stopped[0]
        if len(stopped) >= 2:  # если очередь больше 2, то мы выводим сообщение о её наличии
            await ctx.message.channel.send(
                f'Сейчас играет:\n{stopped[0]}\nследующий:\n{stopped[1]}\n\n```Пропишите *skip для пропуска музыки```')
    if t_f:  # на момент музыки блокирует проигрывание следующей
        try:
            t_f = False
            song_there = os.path.isfile('song.mp3')
            try:
                if song_there:  # Если мы находим остаточный файл с музыкой, мы его удаляем
                    os.remove('song.mp3')
            except PermissionError:
                pass
            await ctx.message.channel.send('Подождите...'
                                           'Если музыка не началась сразу, ждите до 2 минут')
            voice = get(ibio.voice_clients, guild=ctx.guild)
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }],
            }  # задаем значения для работы с библиотекой youtube-dl, а именно загрузку.
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])  # загружаем музыку на наш компьютер
            for file in os.listdir('./'):
                if file.endswith('.mp3'):
                    os.rename(file, 'song.mp3')  # переименовываем наш загруженный файл с музыкой
            voice.play(discord.FFmpegPCMAudio('song.mp3'), after=lambda e: on_off(ctx))  # после окончания запускаем вспомогательную функцию
            voice.source = discord.PCMVolumeTransformer(voice.source)  # запускаем музыку
            voice.source.volume = 1  # выставляем громкость
        except Exception:  # Если ссылка на музыку неправильная, МЫ ЕЁ ИГНОРИРУЕМ И ЗАПУСКАЕМ СЛЕДУЮЩУЮ.
            on_off(ctx)


@ibio.command()
async def skip(ctx):  # при вызове скип, мы останавливаем нашу текущую музыку
    global voice
    await ctx.message.channel.send(f'{stopped[0]} пропущена')
    voice.stop()


@ibio.command()
async def rem(ctx, *arg):  # создание воспоминаний
    author = ctx.message.author
    information = ' '.join(arg)
    if '~~~' not in information and '===' not in information and '+++' not in information:  # проверка на запрещённые символы
        file1 = open('remember_user/all_member_user.txt', mode='rt')  # открывем наш файл со всеми воспоминаниями пользователей
        old_inf = (file1.read()).split('~~~')  # сохраняем воспоминания в список
        print(old_inf)
        file = open('remember_user/all_member_user.txt', mode='w')  # открывем второй файл, но уже для сохранения
        print(str('~~~'.join(old_inf)))
        aut = ''.join(author.mention.split('!'))  # делаем пользователя равным во всех каналах и серверах
        if aut in str('~~~'.join(old_inf)):  # проверяем, есть ли у пользователя воспоминания
            for i in range(1, len(old_inf)):  # ищем в бд воспоминаия пользователя
                if (old_inf[i].split('+++'))[0] == aut:  # если мы их нащ=шли, то...
                    information = str((old_inf[i].split('+++'))[1]) + '===' + information  # добавляем их к старым
                    old_inf[i] = aut + '+++' + information  # и сохраняем в текущих
                    break
            itog = '~~~'.join(old_inf)  # преобразуем файл в исходный вид
            file.write(f'{itog}')  # сохраняем данный файл
            file.close()
        else:  # если воспоминаний пользователь раньше не делал мы создаём новый список для него
            old_inf = '~~~'.join(old_inf)
            file.write(f'{old_inf}~~~{aut}+++{information}')  # создаём новое воспоминание пользователя
            file.close()
        await ctx.message.channel.send(f'{author.mention}, Ваше напоминание запомнено...')  # успех записи
    else:
        await ctx.message.channel.send(f'{author.mention}, ваше напоминание содержит недопустимые символы: ~~~, +++, ===')  # выводим сообщение, что данный символы нельзя использовать


@ibio.command()
async def tell(ctx):  # вывод воспоминаний
    author = ctx.message.author
    file1 = open('remember_user/all_member_user.txt', mode='rt')  # открываем файл с воспоминаниями пользователей
    old_inf = (file1.read()).split('~~~')  # сохраняем их в список
    print(str('~~~'.join(old_inf)))
    aut = ''.join(author.mention.split('!'))  # делаем пользователя равным во всех каналах и серверах
    if aut in str('~~~'.join(old_inf)):  # проверка, есть ли у пользователя напоминания
        for i in range(1, len(old_inf)):
            if (old_inf[i].split('+++'))[0] == aut:  # нашли воспоминания пользователя
                sss = '\n'.join(((old_inf[i].split('+++'))[1]).split('==='))  # преобразум в человеческий вид
                await ctx.message.channel.send(f'Напоминания {author.mention} :\n'
                                               f'```{sss}```')  # и выводим ему на сервер
                break
    else:  # если их нет, то выводим соответсвующее сообщение
        await ctx.message.channel.send(f'{author.mention}, Вы ещё не делали напоминаний')


@ibio.command()
async def code(ctx):  # генератор кода
    location = (os.getcwd()[0:-5]) + r'\сайт\code_users\codes.txt'  # показываем путь до папки с кодами пользователей
    file = open(location, mode='rt')  # читаем коды
    file_sost = file.read()  # сохраняем
    file2 = open(location, mode='w')  # подготавливаем файл для записи
    author = ctx.message.author  # тег автора
    unical_code = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                   'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
                   'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z',
                   'x', 'c', 'v', 'b', 'n', 'm']  # символы допустисые в коде(пароле)
    generate = choice(unical_code) + choice(unical_code) + choice(unical_code) + choice(unical_code) + choice(
        unical_code) + choice(unical_code)  # генерируем рандомно код
    while generate in file_sost:  # если такой код есть у других пользователейЮ то мы его генерируе до тех пор пока он не станет уникальным
        generate = choice(unical_code) + choice(unical_code) + choice(unical_code) + choice(unical_code) + choice(
            unical_code) + choice(unical_code)
    prom = None  # это Нони
    aut = ''.join(author.mention.split('!'))  # делаем пользователя равным по всем каналам и серверам
    if aut in file_sost:  # проверка на то, что есть ли у пользователя код
        prom = file_sost.split('***')  # если код у пользователя есть, то мы его находим и переделывем на новый
        for i in range(1, len(prom)):
            if aut in prom[i]:
                prom[i] = aut + '~' + generate
                break
        prom = '***'.join(prom)  # делаем вид для нашего файла
    else:  # если нет, то создаеём в файле пользователя с новым кодом
        prom = file_sost + '***' + aut + '~' + generate
    file2.write(prom)
    file2.close()
    file.close()
    await ctx.message.author.send('Ваш логин:'
                                  f'```{aut}```'
                                  'Ваш код:'
                                  f'```{generate}```')  # сообщаем пользователю его обновлённые(или просто) данные ЛИЧНО


@ibio.command()
async def addmus(ctx, arg):  # добавление музыки в плей-лист и его создание
    mus = arg
    author = ctx.message.author
    aut = ''.join(author.mention.split('!'))  # преобразум пользователя равным по всем каналам и серверам
    aut = ''.join((''.join(aut.split('<@'))).split('>'))  # лишаем его индексов
    name_file = f'playlist_users/{aut}.txt'  # делаем путь до файла пользователя
    try:  # если файл не найдётся...
        file = open(name_file, mode='rt')  # открываем файл пользователя
        inff = file.read().split('\n')  # сохраняем старые данные
        file.close()
        file = open(name_file, mode='w')  # подготавливаем сохраняемый файл
        inff.append(mus)  # добавляем к старым данным новые
        inff = '\n'.join(inff)  # делаем нормальный, читаемый вид для файла
        file.write(inff)  # сохраняем
        file.close()
        await ctx.message.channel.send('Ссылка на музыку добавлена в ваш плей-лист')
    except Exception:  # мы выведем соообщение, что создали есму новый файл(плей-лист)
        file = open(f'playlist_users/{aut}.txt', mode='w')  # создаём новый файл с пле-лситом пользователя и схраняем туда его первую музыку
        file.write(mus)  # сохраняем
        file.close()
        await ctx.message.channel.send('Создан плей-лист с вашей первой музыкой')


@ibio.command()
async def pp(ctx):  # добавление плей-листа в список очереди
    global t_f, voice, stopped
    try:  # если плей-лист не найден...
        if s_f:  # проверка на активность бота
            author = ctx.message.author
            aut = ''.join(author.mention.split('!'))  # делаем пользователя равным по всем каналам и серверам
            aut = ''.join((''.join(aut.split('<@'))).split('>'))  # лишаем его лишних знаков
            name_file = f'playlist_users/{aut}.txt'  # делаем путь до файла
            file = open(name_file, mode='rt')  # открываем его
            inff = file.read().split('\n')
            for i in range(len(inff)):
                stopped.append(inff[i])  # по очереди добавляем в очередь ссылки из плей-листа
            print(stopped)
            await ctx.message.channel.send('Ваш плей-лист добавлен в очередь\n'
                                           'Для запуска пропишите: *play music')
    except Exception:  # выводим сообщение, что его нет.
        await ctx.message.channel.send('Похоже ваш плей лист пуст!')


@ibio.command()
async def playlist(ctx):  # показ пользователю текущий плей-лист
    try:  # если мы находим пле-лист пользователя, иначе...
        author = ctx.message.author
        aut = ''.join(author.mention.split('!'))  # обычная операция лишения пользователя прав
        aut = ''.join((''.join(aut.split('<@'))).split('>'))  # преобразование пользователя в режим читаемый файлом
        name_file = f'playlist_users/{aut}.txt'
        file = open(name_file, mode='rt')  # ищем файл с плей-листом пользователя
        inff = file.read().split('\n')  # записываем файл в список
        inffile = list()
        for i in range(len(inff)):
            inffile.append(f'{i + 1}. {inff[i]}')  # сохраняем по очереди номера музыки в плей-листе
        inffile = '\n'.join(inffile)  # преобразуем в читаемый вид
        file.close()
        await ctx.message.author.send(f'Плей-лист {author.mention}:\n{inffile}')  # выводим пользователю его плей лист ЛИЧНО
    except Exception:  # сообщаем что его плей-лист не найден
        await ctx.message.author.send('Похоже ваш плей лист пуст!')


@ibio.command()
async def dellist(ctx, *args):  # удаление музыки из плей-листа
    try:  # если у пользователя есть плей-лист и все данные введены верно, иначе...
        author = ctx.message.author
        aut = ''.join(author.mention.split('!'))  # удаляем права пользователя и делаем его равным по всем каналам и серверам
        aut = ''.join((''.join(aut.split('<@'))).split('>'))  # лишаем его лишних символов
        name_file = f'playlist_users/{aut}.txt'  # путь до файла пользователя
        file = open(name_file, mode='rt')  # открываем файл пользователя
        inff = file.read().split('\n')  # сохраняем данные с файла в список
        file.close()
        file = open(name_file, mode='w')  # подготавливаем файл для загрузки
        indel = list()
        for i in range(len(args)):
            indel.append(inff[int(args[i]) - 1])  # добавляем в список удаляемых файлов, что мы хотим удалить, это деаем из-за ошибки, что появляется: list index out of range
        for j in indel:
            inff.remove(j)  # по очереди удаляем из файла ненужные ссылки
        file.write('\n'.join(inff))  # сохраняем данные в файл
        file.close()
        await ctx.message.author.send(f'Плей-лист {author.mention} - успешно обновлён')
    except Exception:  # выводим, что его нет или данные введены не верно
        await ctx.message.author.send('Похоже ваш плей лист пуст или вы превысили в значениях пременных лимит музыки!')


ibio.run(TOKEN)  # запускаем бота по его токену
