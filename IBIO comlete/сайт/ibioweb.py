from flask import Flask, render_template, request, redirect
from flask_ngrok import run_with_ngrok
import json
import requests
import os


def get_ngrok_url():
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
    file = open('url/now_url.txt', mode='w')
    url = (str(get_ngrok_url()).split())[-1]
    file.write(url)
    file.close()
    menu = str(url) + '/register'
    return render_template('base.html', url=menu)


@app.route("/register", methods=['GET', 'POST'])
def reg():
    url = (str(get_ngrok_url()).split())[-1]
    menu = str(url) + '/how'
    if request.method == 'POST':
        file = open('code_users/codes.txt', mode='rt')
        spisok_passwords = file.read().split('***')
        inf = ''.join(request.form['tag'].split()) + '~' + ''.join(request.form['code'].split())
        name = ''.join(request.form['tag'].split())
        file.close()
        if inf in spisok_passwords:
            return redirect(f'/menu/{name}')
        else:
            return redirect('/wrong_password')
    return render_template('register.html', url=menu)


@app.route("/how")
def how():
    url = (str(get_ngrok_url()).split())[-1]
    menu = str(url) + '/register'
    menu2 = str(url) + '/'
    return render_template('how.html', url=menu, url2=menu2)


@app.route('/wrong_password')
def wrong():
    url = (str(get_ngrok_url()).split())[-1]
    menu = str(url) + '/register'
    return render_template('wrong.html', url=menu)


@app.route('/menu/<name>')
def menu(name):
    location = (os.getcwd()[0:-5]) + r'\IBIO\remember_user\all_member_user.txt'
    file = open(location, mode='rt')
    inf_file = file.read().split('~~~')
    file.close()
    information = None
    for i in range(1, len(inf_file)):
        if name in inf_file[i]:
            information = ', '.join(((inf_file[i].split('+++'))[1]).split('==='))
            break
    user = ''.join((''.join(name.split('<@'))).split('>'))
    try:
        location2 = (os.getcwd()[0:-5]) + rf'\IBIO\playlist_users\{user}.txt'
        file = open(location2, mode='rt')
        information2 = ', '.join(file.read().split('\n'))
    except Exception:
        information2 = 'Ваш плей-лист пуст'
    url = (str(get_ngrok_url()).split())[-1]
    menu = str(url) + '/register'
    menu2 = str(url) + '/'
    return render_template('menu.html', url=menu, name=name, url2=menu2, inf=information, inf2=information2)


if __name__ == '__main__':
    app.run()