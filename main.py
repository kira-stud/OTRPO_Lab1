from flask import Flask, render_template, request, redirect, session, abort
import requests
import random
import math
from bd import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cb02820a3e94d72c9f950ee10ef7e3f7a35b3f5b'


@app.route("/")
def index():
    pokies_data = search()

    return render_template("pokies.html", poki=pokies_data)


@app.route("/search")
def search():
    try:
        search = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        per_page = 4
        offset = (page - 1) * per_page

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
        max_page = math.ceil(len(pokies) / per_page)
        pokies = pokies[offset:offset + per_page]

        pokies_data = [[], page, max_page, search]
        for p in pokies:
            poki_url = p['url']
            pokemon = requests.get(poki_url).json()

            pokemon_stats = {
                'name': pokemon['name'],
                'image': pokemon['sprites']['front_default'],
                'attack': pokemon['stats'][1]['base_stat'],
                'hp': pokemon['stats'][0]['base_stat']
            }
            pokies_data[0].append(pokemon_stats)

        return pokies_data
    except:
        return redirect("/")


@app.route("/<poki>")
def pokemon(poki):
    try:
        url = "https://pokeapi.co/api/v2/pokemon/" + poki
        pokemon = requests.get(url)
        if not pokemon.ok:
            return redirect("/")
        pokemon = pokemon.json()
        pokemon_stats = {
            'name': pokemon['name'],
            'image': pokemon['sprites']['front_default'],
            'attack': pokemon['stats'][1]['base_stat'],
            'hp': pokemon['stats'][0]['base_stat'],
            'type': pokemon['types'][0]['type']['name'],
            'height': pokemon['height'],
            'weight': pokemon['weight']
        }

        return render_template("poki.html", poki=pokemon_stats)
    except:
        return redirect("/")


@app.route("/<poki>/fight")
def fight(poki):
    try:
        name = poki
        url = "https://pokeapi.co/api/v2/pokemon/" + poki
        pokemon = requests.get(url)
        if not pokemon.ok:
            return redirect("/")
        pokemon = pokemon.json()

        pokies = []

        player_poki = {
            'name': name,
            'image': pokemon['sprites']['front_default'],
            'attack': pokemon['stats'][1]['base_stat'],
            'hp': pokemon['stats'][0]['base_stat']
        }
        pokies.append(player_poki)

        url = 'https://pokeapi.co/api/v2/pokemon/'
        count = requests.get(url).json()['count']
        bot_num = random.randint(1, count)
        bot_url = requests.get(url, params={'limit': 1, 'offset': bot_num - 1}).json()['results'][0]['url']
        bot = requests.get(bot_url).json()
        bot_poki = {
            'name': bot['name'],
            'image': bot['sprites']['front_default'],
            'attack': bot['stats'][1]['base_stat'],
            'hp': bot['stats'][0]['base_stat']
        }
        pokies.append(bot_poki)
        session['hp'] = player_poki['hp']
        session['bot_hp'] = bot_poki['hp']
        session['attack'] = player_poki['attack']
        session['bot_attack'] = bot_poki['attack']
        session['poki'] = poki
        session['bot_poki'] = bot_poki['name']

        return render_template("fight.html", poki=pokies)
    except:
        return redirect("/")


@app.route("/attack")
def attack():
        val = request.args.get('val', -1, type=int)
        if val < 1 or val > 10 or len(session) < 6:
            abort(404)
        bot_val = random.randint(1, 10)
        if bot_val % 2 != val % 2:
            session['hp'] -= session['bot_attack']
        else:
            session['bot_hp'] -= session['attack']
        stats = {
            "hp": session['hp'],
            "bot_hp": session['bot_hp'],
            "attack": session['attack'],
            "bot_attack": session['bot_attack'],
            "bot_val": bot_val
        }
        if session['hp'] <= 0 or session['bot_hp'] <= 0:
            player_res = 1 if session['bot_hp'] <= 0 else 0
            fight = Fight(session['poki'], session['bot_poki'], player_res, 1-player_res)
            sess.add(fight)
            sess.commit()
            try:
                pass
            except:
                sess.rollback()

            session.pop("hp", None)
            session.pop("bot_hp", None)
            session.pop("attack", None)
            session.pop("bot_attack", None)
            session.pop("poki", None)
            session.pop("bot_poki", None)

        return stats


if __name__ == "__main__":
    app.run(debug=True)
