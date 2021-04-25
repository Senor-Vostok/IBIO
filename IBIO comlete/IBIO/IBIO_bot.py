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
async def ready(ctx):
    global t_f, s_f
    await ctx.message.channel.send('```IBIO``` подключён.')
    await ctx.message.author.voice.channel.connect(reconnect=True)
    t_f = True
    s_f = True


@ibio.command()
async def IBIO_help(ctx):
    location = (os.getcwd()[0:-5]) + r'\сайт\url\now_url.txt'
    file = open(location, mode='rt')
    url = file.read()
    await ctx.message.channel.send('```IBIO комманды:\n'
                                   'ready - вкл/выкл бот\n'
                                   'clarify "исчесление времени" - говорит время\n'
                                   'play "ссылка на видео с ютуба" - проигрывает музыку\n'
                                   'rem "Любые символы" - запоминает вашу фразу\n'
                                   'tell - воспроизводит ваши воспоминания\n'
                                   '\n'
                                   '\n'
                                   f'Все комманды находятся на нашем сайте``` {url}')


@ibio.command()
async def clarify(ctx, args):
    arg = (''.join((''.join(args.split('('))).split(')'))).lower()
    day = int((str((datetime.datetime.now().date())).split('-'))[2])
    month = const_month[int((str((datetime.datetime.now().date())).split('-'))[1])]
    year = int((str((datetime.datetime.now().date())).split('-'))[0])
    if arg == 'дата':
        await ctx.message.channel.send(f'```{day} {month} {year} год.```')
    elif arg == 'время':
        await ctx.message.channel.send(f'```{datetime.datetime.now().hour}:{datetime.datetime.now().minute}```')


def on_off(ctx):
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
async def play(ctx, url='False'):
    global t_f, voice, stopped
    if s_f:
        if url != 'music':
            stopped.append(url)
        print(stopped)
        url = stopped[0]
        if len(stopped) >= 2:
            await ctx.message.channel.send(f'Сейчас играет:\n{stopped[0]}\nследующий:\n{stopped[1]}\n\n```Пропишите *skip для пропуска музыки```')
    if t_f:
        try:
            t_f = False
            song_there = os.path.isfile('song.mp3')
            try:
                if song_there:
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
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                try:
                    await ctx.message.author.voice.channel.connect(reconnect=True)
                except Exception:
                    pass
            for file in os.listdir('./'):
                if file.endswith('.mp3'):
                    os.rename(file, 'song.mp3')
            voice.play(discord.FFmpegPCMAudio('song.mp3'), after=lambda e: on_off(ctx))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 1
        except Exception:
            on_off(ctx)


@ibio.command()
async def skip(ctx):
    global voice
    await ctx.message.channel.send(f'{stopped[0]} пропущена')
    voice.stop()


@ibio.command()
async def rem(ctx, *arg):
    author = ctx.message.author
    information = ' '.join(arg)
    if '~~~' not in information and '===' not in information and '+++' not in information:
        file1 = open('remember_user/all_member_user.txt', mode='rt')
        old_inf = (file1.read()).split('~~~')
        print(old_inf)
        file = open('remember_user/all_member_user.txt', mode='w')
        print(str('~~~'.join(old_inf)))
        aut = ''.join(author.mention.split('!'))
        if aut in str('~~~'.join(old_inf)):
            for i in range(1, len(old_inf)):
                if (old_inf[i].split('+++'))[0] == aut:
                    information = str((old_inf[i].split('+++'))[1]) + '===' + information
                    old_inf[i] = aut + '+++' + information
                    break
            itog = '~~~'.join(old_inf)
            file.write(f'{itog}')
            file.close()
        else:
            old_inf = '~~~'.join(old_inf)
            file.write(f'{old_inf}~~~{aut}+++{information}')
            file.close()
        await ctx.message.channel.send(f'{author.mention}, Ваше напоминание запомнено...')
    else:
        await ctx.message.channel.send(f'{author.mention}, ваше напоминание содержит недопустимые символы: ~~~')


@ibio.command()
async def tell(ctx):
    author = ctx.message.author
    file1 = open('remember_user/all_member_user.txt', mode='rt')
    old_inf = (file1.read()).split('~~~')
    print(str('~~~'.join(old_inf)))
    aut = ''.join(author.mention.split('!'))
    if aut in str('~~~'.join(old_inf)):
        for i in range(1, len(old_inf)):
            if (old_inf[i].split('+++'))[0] == aut:
                sss = '\n'.join(((old_inf[i].split('+++'))[1]).split('==='))
                await ctx.message.channel.send(f'Напоминания {author.mention} :\n'
                                               f'```{sss}```')
                break
    else:
        await ctx.message.channel.send(f'{author.mention}, Вы ещё не делали напоминаний')


@ibio.command()
async def code(ctx):
    location = (os.getcwd()[0:-5]) + r'\сайт\code_users\codes.txt'
    file = open(location, mode='rt')
    file_sost = file.read()
    file2 = open(location, mode='w')
    author = ctx.message.author
    unical_code = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                   'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
                   'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z',
                   'x', 'c', 'v', 'b', 'n', 'm']
    generate = choice(unical_code) + choice(unical_code) + choice(unical_code) + choice(unical_code) + choice(unical_code) + choice(unical_code)
    while generate in file_sost:
        generate = choice(unical_code) + choice(unical_code) + choice(unical_code) + choice(unical_code) + choice(unical_code) + choice(unical_code)
    prom = None
    aut = ''.join(author.mention.split('!'))
    if aut in file_sost:
        prom = file_sost.split('***')
        for i in range(1, len(prom)):
            if aut in prom[i]:
                prom[i] = aut + '~' + generate
                break
        prom = '***'.join(prom)
    else:
        prom = file_sost + '***' + aut + '~' + generate
    file2.write(prom)
    file2.close()
    file.close()
    await ctx.message.author.send('Ваш логин:'
                                  f'```{aut}```'
                                  'Ваш код:'
                                  f'```{generate}```')


@ibio.command()
async def addmus(ctx, arg):
    mus = arg
    author = ctx.message.author
    aut = ''.join(author.mention.split('!'))
    aut = ''.join((''.join(aut.split('<@'))).split('>'))
    name_file = f'playlist_users/{aut}.txt'
    try:
        file = open(name_file, mode='rt')
        inff = file.read().split('\n')
        file.close()
        file = open(name_file, mode='w')
        inff.append(mus)
        inff = '\n'.join(inff)
        file.write(inff)
        file.close()
        await ctx.message.channel.send('Ссылка на музыку добавлена в ваш плей-лист')
    except Exception:
        file = open(f'playlist_users/{aut}.txt', mode='w')
        file.write(mus)
        file.close()
        await ctx.message.channel.send('Создан плей-лист с вашей первой музыкой')


@ibio.command()
async def pp(ctx):
    global t_f, voice, stopped
    try:
        if s_f:
            author = ctx.message.author
            aut = ''.join(author.mention.split('!'))
            aut = ''.join((''.join(aut.split('<@'))).split('>'))
            name_file = f'playlist_users/{aut}.txt'
            file = open(name_file, mode='rt')
            inff = file.read().split('\n')
            for i in range(len(inff)):
                stopped.append(inff[i])
            print(stopped)
            await ctx.message.channel.send('Ваш плей-лист добавлен в очередь\n'
                                           'Для запуска пропишите: *play music')
    except Exception:
        await ctx.message.channel.send('Похоже ваш плей лист пуст!')


@ibio.command()
async def playlist(ctx):
    try:
        author = ctx.message.author
        aut = ''.join(author.mention.split('!'))
        aut = ''.join((''.join(aut.split('<@'))).split('>'))
        name_file = f'playlist_users/{aut}.txt'
        file = open(name_file, mode='rt')
        inff = file.read().split('\n')
        inffile = list()
        for i in range(len(inff)):
            inffile.append(f'{i + 1}. {inff[i]}')
        inffile = '\n'.join(inffile)
        file.close()
        await ctx.message.author.send(f'Плей-лист {author.mention}:\n{inffile}')
    except Exception:
        await ctx.message.author.send('Похоже ваш плей лист пуст!')


@ibio.command()
async def dellist(ctx, *args):
    try:
        author = ctx.message.author
        aut = ''.join(author.mention.split('!'))
        aut = ''.join((''.join(aut.split('<@'))).split('>'))
        name_file = f'playlist_users/{aut}.txt'
        file = open(name_file, mode='rt')
        inff = file.read().split('\n')
        file.close()
        file = open(name_file, mode='w')
        indel = list()
        for i in range(len(args)):
            indel.append(inff[int(args[i]) - 1])
        for j in indel:
            inff.remove(j)
        file.write('\n'.join(inff))
        file.close()
        await ctx.message.author.send(f'Плей-лист {author.mention} - успешно обновлён')
    except Exception:
        await ctx.message.author.send('Похоже ваш плей лист пуст!')


ibio.run(TOKEN)