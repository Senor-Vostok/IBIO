from flask import Flask, render_template, request, redirect
from flask_ngrok import run_with_ngrok
import json
import requests
import os


def get_ngrok_url():  # Такой полезной функции я в жизни не виде(она выдаёт адресс запущенного сервера ngrok)
    url = "http://localhost:4040/api/tunnels/"
    res = requests.get(url)
    res_unicode = res.content.decode("utf-8")
    res_json = json.loads(res_unicode)
    for i in res_json["tunnels"]:
        if i['name'] == 'command_line':
            return i['public_url']


app = Flask(__name__)
run_with_ngrok(app)


@app.route("/")
def index():
    file = open('url/now_url.txt', mode='w')  # при первом запуске страницы мы сохраняем в отдельный файл ссылку на адресс
    url = (str(get_ngrok_url()).split())[-1]
    file.write(url)
    file.close()
    menu = str(url) + '/register'  # делаем ссылку на нашу новую вкладку
    return render_template('base.html', url=menu)


@app.route("/register", methods=['GET', 'POST'])
def reg():
    url = (str(get_ngrok_url()).split())[-1]  # получаем теущий адресс страницы(главной)
    menu = str(url) + '/how'
    if request.method == 'POST':  # если заполнили регистрацию на сайте
        file = open('code_users/codes.txt', mode='rt')  # открывеем файл с кодами пользователей и сверяем их подлинность с введёнными
        spisok_passwords = file.read().split('***')
        inf = ''.join(request.form['tag'].split()) + '~' + ''.join(request.form['code'].split())
        name = ''.join(request.form['tag'].split())
        file.close()
        if inf in spisok_passwords:
            return redirect(f'/menu/{name}')  # если всё прошло хорошо, то перенапрвляем пользователя на его страницу
        else:
            return redirect('/wrong_password')  # иначе выходим на страницу с ошибкой
    return render_template('register.html', url=menu)  # запускаем вкладку входа


@app.route("/how")
def how():
    url = (str(get_ngrok_url()).split())[-1]
    menu = str(url) + '/register'  # передаём ссылки на две страницы(на регистрацию и меню)
    menu2 = str(url) + '/'
    return render_template('how.html', url=menu, url2=menu2)  # запускаем окно "как получить код?"


@app.route('/wrong_password')
def wrong():
    url = (str(get_ngrok_url()).split())[-1]
    menu = str(url) + '/register'  # ссылка на страницу регистрации
    return render_template('wrong.html', url=menu)  # выводим страницу с надписью о неправильности кода или логина


@app.route('/menu/<name>')
def menu(name):
    location = (os.getcwd()[0:-5]) + r'\IBIO\remember_user\all_member_user.txt'  # передаём адресс до воспоминаний пользователей
    file = open(location, mode='rt')  #  открывем файл с воспоминаиями
    inf_file = file.read().split('~~~')  # сохраняем данные в список
    file.close()
    information = 'Вы еще не делали воспоминаний'  # задаём стартовое значение о всех воспоминаниях
    for i in range(1, len(inf_file)):  # проверяем все воспоминаия
        if name in inf_file[i]:  # если мы нашли воспоминания пользователя, то записываем их в нашу, заранее созданную переменную
            information = ', '.join(((inf_file[i].split('+++'))[1]).split('==='))
            break
    user = ''.join((''.join(name.split('<@'))).split('>'))  # полчаем имя пользователя из списка воспоминаий
    try:
        location2 = (os.getcwd()[0:-5]) + rf'\IBIO\playlist_users\{user}.txt'  # ищем файл с пле-листом пользователя
        file = open(location2, mode='rt')  # открываем его
        information2 = ', '.join(file.read().split('\n'))  # записываем все ссылки через запятую
    except Exception:  # если мы не нашли пле-лист пользователя, то в переменную записываем, что плей-лист пуст
        information2 = 'Ваш плей-лист пуст'
    url = (str(get_ngrok_url()).split())[-1]
    menu = str(url) + '/register'  # ссылка на регистрацию
    menu2 = str(url) + '/'  # ссылк ана главное меню
    return render_template('menu.html', url=menu, name=name, url2=menu2, inf=information, inf2=information2)  # запускаем нашу страницу с данными о пользователе


if __name__ == '__main__':
    app.run()  # запускаем наш сайт
