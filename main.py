from flask import Flask, render_template, request, session, abort, redirect
from flask_restful import Api, Resource
import requests
import random
import math
from bd import *
import json
import smtplib
import ssl
from letter import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ftplib
import datetime
import io
import redis
from passlib.context import CryptContext
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
api = Api(app)
oauth = OAuth()
yandex = oauth.remote_app(
                'yandex',
                consumer_key=YANDEX_CLIENT_ID,
                consumer_secret=YANDEX_CLIENT_SECRET,
                request_token_params={'scope': 'login:email'},
                base_url='https://login.yandex.ru/',
                request_token_url=None,
                access_token_method='POST',
                access_token_url='https://oauth.yandex.ru/token',
                authorize_url='https://oauth.yandex.ru/authorize'
            )

pwd_context = CryptContext(schemes=["argon2"])

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


class PokemonApi(Resource):
    def get(self):
        try:
            search = request.args.get('search', '')
            page = request.args.get('page', 1, type=int)
            page = max(1, page)

            cache_key = "all" + str(page) + "_" + str(search)
            cache_res = redis_client.get(cache_key)
            if cache_res is not None:
                return json.loads(cache_res)

            pokies0 = []
            url = 'https://pokeapi.co/api/v2/pokemon'
            count = requests.get(url).json()['count']
            response = requests.get(url, params={'limit': count})
            if response.status_code == 200:
                pokies0.extend(response.json()['results'])
            pokies = []
            if search != "":
                for p in pokies0:
                    if search in p['name']:
                        pokies.append(p)
            else:
                pokies = pokies0

            per_page = 4
            max_page = math.ceil(len(pokies) / per_page)
            page = min(max_page, page)
            offset = (page - 1) * per_page
            pokies = pokies[offset:offset + per_page]

            pokies_data = {"pokemons": [], "page": page, "max_page": max_page, "search": search}
            for p in pokies:
                poki_url = p['url']
                pokemon = requests.get(poki_url).json()

                pokemon_stats = {
                    'id': pokemon['id'],
                    'name': pokemon['name'],
                    'image': pokemon['sprites']['front_default'],
                    'attack': pokemon['stats'][1]['base_stat'],
                    'hp': pokemon['stats'][0]['base_stat']
                }
                pokies_data["pokemons"].append(pokemon_stats)

            redis_client.set(cache_key, json.dumps(pokies_data))
            redis_client.expire(cache_key, 3600)

            return pokies_data
        except:
            return {"pokemons": [], "page": 1, "max_page": 1, "search": ""}


class Poki(Resource):
    def get(self, id):
        try:
            cache_key = str(id)
            cache_res = redis_client.get(cache_key)
            if cache_res:
                return json.loads(cache_res)

            url = "https://pokeapi.co/api/v2/pokemon/" + str(id)
            pokemon = requests.get(url)
            if not pokemon.ok:
                pokemon_stats = {
                    'id': id,
                    'name': "unknown",
                    'image': "unknown",
                    'attack': "unknown",
                    'hp': "unknown",
                    'type': "unknown",
                    'height': "unknown",
                    'weight': "unknown"
                }
            else:
                pokemon = pokemon.json()
                pokemon_stats = {
                    'id': pokemon['id'],
                    'name': pokemon['name'],
                    'image': pokemon['sprites']['front_default'],
                    'attack': pokemon['stats'][1]['base_stat'],
                    'hp': pokemon['stats'][0]['base_stat'],
                    'type': pokemon['types'][0]['type']['name'],
                    'height': pokemon['height'],
                    'weight': pokemon['weight']
                }
            redis_client.set(cache_key, json.dumps(pokemon_stats))
            redis_client.expire(cache_key, 3600)

            return pokemon_stats
        except:
            return {
                    'id': id,
                    'name': "unknown",
                    'image': "unknown",
                    'attack': "unknown",
                    'hp': "unknown",
                    'type': "unknown",
                    'height': "unknown",
                    'weight': "unknown"
                }


class Rand(Resource):
    def get(self):
        try:
            url = 'https://pokeapi.co/api/v2/pokemon/'
            count = requests.get(url).json()['count']
            bot_num = random.randint(1, count)
            bot_id = requests.get(url, params={'limit': 1, 'offset': bot_num - 1}).json()['results'][0]['url'].split('/')[-2]

            return {"id": bot_id}
        except:
            return {"id": 1}


class Fighting(Resource):
    def get(self):
        try:
            user_id = request.args.get('user_id', 1, type=int)
            bot_id = request.args.get('bot_id', 1, type=int)
            url = "https://pokeapi.co/api/v2/pokemon/" + str(user_id)
            pokemon = requests.get(url)
            if not pokemon.ok:
                player_poki = {
                    'name': "unknown",
                    'image': "unknown",
                    'attack': 1,
                    'hp': 1
                }
            else:
                pokemon = pokemon.json()
                player_poki = {
                    'name': pokemon['name'],
                    'image': pokemon['sprites']['front_default'],
                    'attack': pokemon['stats'][1]['base_stat'],
                    'hp': pokemon['stats'][0]['base_stat']
                }

            bot_url = 'https://pokeapi.co/api/v2/pokemon/' + str(bot_id)
            bot = requests.get(bot_url)
            if not bot.ok:
                bot_poki = {
                    'name': "unknown",
                    'image': "unknown",
                    'attack': 1,
                    'hp': 1
                }
            else:
                bot = bot.json()
                bot_poki = {
                    'name': bot['name'],
                    'image': bot['sprites']['front_default'],
                    'attack': bot['stats'][1]['base_stat'],
                    'hp': bot['stats'][0]['base_stat']
                }

            session['hp'] = player_poki['hp']
            session['bot_hp'] = bot_poki['hp']
            session['attack'] = player_poki['attack']
            session['bot_attack'] = bot_poki['attack']
            session['id'] = user_id
            session['bot_id'] = bot_id
            session['name'] = player_poki['name']
            session['bot_name'] = bot_poki['name']
            session['image'] = player_poki['image']
            session['bot_image'] = bot_poki['image']
            session['rounds'] = []

            return {"player_poki": player_poki, "bot_poki": bot_poki}
        except:
            return {"player_poki": {'name': "unknown", 'image': "unknown", 'attack': 1, 'hp': 1},
                    "bot_poki": {'name': "unknown", 'image': "unknown", 'attack': 1, 'hp': 1}}


class Attack(Resource):
    def post(self, val):
        if len(session) < 11:
            abort(404)
        elif val < 1 or val > 10:
            player_poki = {
                'id': session['id'],
                'name': session['name'],
                'image': session['image'],
                'attack': session['attack'],
                'hp': session['hp'],
                'val': val
            }
            bot_poki = {
                'id': session['bot_id'],
                'name': session['bot_name'],
                'image': session['bot_image'],
                'attack': session['bot_attack'],
                'hp': session['bot_hp'],
                'val': -1
            }
            return {"player_poki": player_poki, "bot_poki": bot_poki, "rounds": session['rounds']}
        try:
            bot_val = random.randint(1, 10)
            session['rounds'].append(f"{val} vs {bot_val}")
            if bot_val % 2 != val % 2:
                session['hp'] -= session['bot_attack']
            else:
                session['bot_hp'] -= session['attack']
            player_poki = {
                'id': session['id'],
                'name': session['name'],
                'image': session['image'],
                'attack': session['attack'],
                'hp': session['hp'],
                'val': val
            }
            bot_poki = {
                'id': session['bot_id'],
                'name': session['bot_name'],
                'image': session['bot_image'],
                'attack': session['bot_attack'],
                'hp': session['bot_hp'],
                'val': bot_val
            }
            rounds = session["rounds"]

            if session['hp'] <= 0 or session['bot_hp'] <= 0:
                res = session['id'] if session['bot_hp'] <= 0 else session['bot_id']
                user_id = None
                if 'user_id' in session:
                    user_id = session['user_id']
                fight = Fight(user_id, session['id'], session['bot_id'], res, len(rounds))
                sess.add(fight)
                sess.commit()
                try:
                    pass
                except:
                    sess.rollback()
                if 'user_id' in session:
                    user_id = session['user_id']
                    session.clear()
                    session['user_id'] = user_id
                else:
                    session.clear()
                return {"player_poki": player_poki, "bot_poki": bot_poki, "rounds": rounds, "fight_id": fight.id}

            return {"player_poki": player_poki, "bot_poki": bot_poki, "rounds": rounds}
        except:
            return {"player_poki": {'name': "unknown", 'image': "unknown", 'attack': 1, 'hp': 1, "val": -1},
                    "bot_poki": {'name': "unknown", 'image': "unknown", 'attack': 1, 'hp': 1, "val": -1},
                    "rounds": []}


class Fast(Resource):
    def get(self):
        if len(session) < 11:
            abort(404)
        try:
            hp = session['hp']
            bot_hp = session['bot_hp']
            attack = session['attack']
            bot_attack = session['bot_attack']
            id = session['id']
            bot_id = session['bot_id']
            rounds = []

            player = {
                'id': id,
                'name': session['name'],
                'image': session['image'],
                'attack': session['attack']
            }
            bot = {
                'id': bot_id,
                'name': session['bot_name'],
                'image': session['bot_image'],
                'attack': session['bot_attack']
            }
            if 'user_id' in session:
                user_id = session['user_id']
                session.clear()
                session['user_id'] = user_id
            else:
                session.clear()

            while hp > 0 and bot_hp > 0:
                val = random.randint(1, 10)
                bot_val = random.randint(1, 10)
                if bot_val % 2 != val % 2:
                    hp -= bot_attack
                else:
                    bot_hp -= attack
                rounds.append(f"{val} vs {bot_val}")
            player['hp'] = hp
            bot['hp'] = bot_hp

            res = id if bot_hp <= 0 else bot_id
            user_id = None
            if 'user_id' in session:
                user_id = session['user_id']
            fight = Fight(user_id, id, bot_id, res, len(rounds))
            sess.add(fight)
            sess.commit()
            try:
                pass
            except:
                sess.rollback()

            return {"player_poki": player, "bot_poki": bot, "rounds": rounds, "fight_id": fight.id}
        except:
            return {"player_poki": {'name': "unknown", 'image': "unknown", 'attack': 1, 'hp': 1},
                    "bot_poki": {'name': "unknown", 'image': "unknown", 'attack': 1, 'hp': 1},
                    "rounds": [],
                    "fight_id": -1}


class SendMail(Resource):
    def post(self):
        try:
            data = request.get_json()

            email = EMAIL
            password = EMAIL_PSW
            to_email = data["email"]

            message = MIMEMultipart('alternative')
            message['Subject'] = 'Результат боя'
            message['From'] = email
            message['To'] = to_email

            fight = sess.query(Fight).filter_by(id=int(data["id"])).first()

            text = "Покемоньи бои"
            html = html_template.format(fight.date_time, fight.player_id, fight.bot_id, fight.winner_id, fight.rounds_count)
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)

            context = ssl.create_default_context()

            server = smtplib.SMTP('smtp.mail.ru', 25)
            server.starttls(context=context)
            server.login(email, password)
            server.sendmail(email, to_email, message.as_string())
            server.quit()

            response_data = {"message": "ОК"}

            return response_data
        except:
            response_data = {"message": "ERROR"}
            return response_data


class SaveData(Resource):
    def post(self, id):
        try:
            ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PSW)
            date = datetime.datetime.now().strftime('%Y%m%d')
            try:
                ftp.mkd(date)
            except:
                pass
            ftp.cwd(date)
            poki = Poki().get(id)

            content = f"# {poki['name']}\n### Характеристики\n* Здоровье: {poki['hp']}\n* Атака: {poki['attack']}\n"
            content += f"* Тип: {poki['type']}\n* Рост: {poki['height']}\n* Вес: {poki['hp']}"
            byte = content.encode('utf-8')
            ftp.storlines(f'STOR {poki["name"]}.md', fp=io.BytesIO(byte))
            ftp.quit()
            return {"message": "OK"}
        except:
            return {"message": "ERROR"}


def send_code(code, send_to):
    try:
        email = EMAIL
        password = EMAIL_PSW
        to_email = send_to

        message = MIMEMultipart('alternative')
        message['Subject'] = 'Код подтверждения'
        message['From'] = email
        message['To'] = to_email

        text = "Вы уверены, что это вы?"
        html = code_html_template.format(code)
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        context = ssl.create_default_context()

        server = smtplib.SMTP('smtp.mail.ru', 25)
        server.starttls(context=context)
        server.login(email, password)
        server.sendmail(email, to_email, message.as_string())
        server.quit()

        return {"message": "OK", 'email': send_to}
    except:
        return {"message": "ERROR"}


class SignUp(Resource):
    def post(self):
        try:
            data = request.get_json()
            user = sess.query(User).filter_by(email=data['email']).first()
            if user is not None and user.password != 'koko':
                return {"message": "EXISTED"}

            p_hash = pwd_context.hash(data['password'])
            code = ""
            for i in range(6):
                code += str(random.randint(0, 9))
            val = {"password": p_hash, "code": pwd_context.hash(code)}
            if user is not None:
                val = {"password": p_hash, "code": pwd_context.hash(code), "change": "yes"}
            redis_client.set(data['email'], json.dumps(val))
            redis_client.expire(data['email'], 300)
            session['email'] = data['email']
            return send_code(code, data['email'])
        except:
            return {"message": "ERROR"}


class SignIn(Resource):
    def post(self):
        try:
            data = request.get_json()
            user = sess.query(User).filter_by(email=data['email']).first()
            if user is None or user.password == "koko" or not pwd_context.verify(data['password'], user.password):
                return {"message": "INCORRECT"}
            code = ""
            for i in range(6):
                code += str(random.randint(0, 9))
            redis_client.set(data['email'], json.dumps({"code": pwd_context.hash(code)}))
            redis_client.expire(data['email'], 300)
            session['email'] = data['email']
            return send_code(code, data['email'])
        except:
            return {"message": "ERROR"}


class SignForgot(Resource):
    def post(self):
        try:
            data = request.get_json()
            user = sess.query(User).filter_by(email=data['email']).all()
            if len(user) == 0:
                return {"message": "NOT FOUND"}
            p_hash = pwd_context.hash(data['password'])
            code = ""
            for i in range(6):
                code += str(random.randint(0, 9))
            redis_client.set(data['email'],
                             json.dumps({"password": p_hash, "code": pwd_context.hash(code), "change": "yes"}))
            redis_client.expire(data['email'], 300)
            session['email'] = data['email']
            return send_code(code, data['email'])
        except:
            return {"message": "ERROR"}


class SignConfirm(Resource):
    def post(self, code):
        try:
            if 'email' not in session:
                return {"message": "INCORRECT"}
            data = json.loads(redis_client.get(session['email']))
            if not pwd_context.verify(code, data['code']):
                return {"message": "INCORRECT"}
            user = sess.query(User).filter_by(email=session['email']).first()
            if user is not None and "change" not in data:
                session.clear()
                session['user_id'] = user.id
                return {"message": "OK", 'user_id': user.id}
            elif "change" in data:
                user = sess.query(User).filter_by(email=session['email'])
                user.update({"password": data['password']})
                sess.commit()
                session.clear()
                user_id = user.first().id
                session['user_id'] = user_id
                return {"message": "OK", 'user_id': user_id}
            else:
                user = User(session['email'], data['password'])
                sess.add(user)
                sess.commit()
                session.clear()
                session['user_id'] = user.id
                return {"message": "OK", 'user_id': user.id}
        except:
            return {"message": "ERROR"}


class SignOut(Resource):
    def post(self):
        try:
            session.pop('user_id', None)
            return {"message": "OK"}
        except:
            return {"message": "ERROR"}


@app.route("/")
def index():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    with app.test_request_context("/pokemon/list", query_string={'search': search, 'page': page}):
        response = app.dispatch_request()
        pokies_data = response.get_json()
    user = session['user_id'] if 'user_id' in session else "None"

    return render_template("pokies.html", poki=pokies_data, user=user)


@app.route("/poki/<id>")
def pokemon(id):
    page = request.args.get("page", 1)
    search = request.args.get("search", "")
    pokemon_stats = Poki().get(id)
    pokemon_stats['page'] = page
    pokemon_stats['search'] = search
    return render_template("poki.html", poki=pokemon_stats)


@app.route("/<int:id>/fight")
def fight(id):
    bot_id = Rand().get()['id']
    with app.test_request_context("/fight", query_string={'user_id': id, 'bot_id': bot_id}):
        response = app.dispatch_request()
        pokies = response.get_json()

    session['hp'] = pokies["player_poki"]['hp']
    session['bot_hp'] = pokies["bot_poki"]['hp']
    session['attack'] = pokies["player_poki"]['attack']
    session['bot_attack'] = pokies["bot_poki"]['attack']
    session['id'] = id
    session['bot_id'] = bot_id
    session['name'] = pokies["player_poki"]['name']
    session['bot_name'] = pokies["bot_poki"]['name']
    session['image'] = pokies["player_poki"]['image']
    session['bot_image'] = pokies["bot_poki"]['image']
    session['rounds'] = []

    return render_template("fight.html", poki=pokies)


@app.route("/attack", methods=['POST'])
def attacka():
    val = request.form.get('val', 1, type=int)
    stats = Attack().post(val)
    return render_template("fight.html", poki=stats)


@app.route("/autofight")
def auto_fight():
    stats = Fast().get()
    return render_template("fight.html", poki=stats)


@app.route("/sign/up", methods=['GET', 'POST'])
def sign_up():
    if request.method == "GET":
        return render_template("sign_up.html")

    email = request.form.get('email')
    password = request.form.get('psw')
    if email is None or password is None:
        return redirect('/sign/up')
    data = {
        'email': email,
        'password': password
    }
    host = request.host_url
    headers = {'Content-Type': 'application/json'}
    response = requests.post(host + "/signup", data=json.dumps(data), headers=headers)
    result = response.json()
    if result['message'] == "OK":
        session['email'] = result['email']
        return redirect('/sign/confirm')
    return redirect('/')


@app.route("/sign/in", methods=['GET', 'POST'])
def sign_in():
    if request.method == "GET":
        return render_template("sign_in.html")

    email = request.form.get('email')
    password = request.form.get('psw')
    if email is None or password is None:
        return redirect('/sign/in')
    data = {
        'email': email,
        'password': password
    }
    host = request.host_url
    headers = {'Content-Type': 'application/json'}
    response = requests.post(host + "/signin", data=json.dumps(data), headers=headers)
    result = response.json()
    if result['message'] == "OK":
        session['email'] = result['email']
        return redirect('/sign/confirm')

    return redirect('/sign/in')


@app.route("/log/in", methods=['POST'])
def log_in():
    return yandex.authorize(callback='http://localhost/log/auth')


@app.route("/log/auth", methods=['GET', 'POST'])
def authorize():
    response = yandex.authorized_response()
    if response is None or 'access_token' not in response:
        return redirect('/sign/in')

    token = response['access_token']
    params = {
        'format': 'json',
        'oauth_token': token
    }
    resp = requests.get('https://login.yandex.ru/info', params=params)

    email = resp.json()['default_email']

    user = sess.query(User).filter_by(email=email).first()
    if user is not None:
        session['user_id'] = user.id
    else:
        user = User(email, 'koko')
        sess.add(user)
        sess.commit()
        session['user_id'] = user.id
    return redirect('/')


@app.route("/forgot", methods=['GET', 'POST'])
def forgot():
    if request.method == "GET":
        return render_template("forgot.html")

    email = request.form.get('email')
    password = request.form.get('psw')
    if email is None or password is None:
        return redirect('/forgot')
    data = {
        'email': email,
        'password': password
    }
    host = request.host_url
    headers = {'Content-Type': 'application/json'}
    response = requests.post(host + "/signforgot", data=json.dumps(data), headers=headers)
    result = response.json()
    if result['message'] == "OK":
        session['email'] = result['email']
        return redirect('/sign/confirm')

    return redirect('/forgot')


@app.route("/sign/confirm", methods=['GET', 'POST'])
def sign_confirm():
    if request.method == "GET":
        return render_template("sign_confirm.html")

    code = request.form.get('code')
    if code is None:
        return redirect('/sign/confirm')

    result = SignConfirm().post(code)
    if result['message'] == "OK":
        session['user_id'] = result['user_id']
        return redirect('/')
    return redirect('/sign/confirm')


@app.route("/sign/out", methods=['POST'])
def sign_out():
    result = SignOut().post()
    if result['message'] == "OK":
        session.pop('user_id', None)
    return redirect('/')


api.add_resource(PokemonApi, '/pokemon/list')
api.add_resource(Poki, '/pokemon/<int:id>')
api.add_resource(Rand, '/pokemon/random')
api.add_resource(Fighting, '/fight')
api.add_resource(Attack, '/fight/<int:val>')
api.add_resource(Fast, '/fight/fast')
api.add_resource(SendMail, '/send_mail')
api.add_resource(SaveData, '/save/<int:id>')
api.add_resource(SignUp, '/signup')
api.add_resource(SignIn, '/signin')
api.add_resource(SignForgot, '/signforgot')
api.add_resource(SignConfirm, '/signconfirm/<code>')
api.add_resource(SignOut, '/signout')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
