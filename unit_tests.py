import unittest
from main import app, sess, Fight, EMAIL
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from chromedriver_py import binary_path


class TestPokemonList(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_count(self):
        response = self.app.get('/pokemon/list', query_string={'search': '', 'page': 1})
        self.assertEqual(len(response.json['pokemons']), 4)
        response2 = self.app.get('/pokemon/list', query_string={'search': 'нет такого', 'page': 1})
        self.assertEqual(len(response2.json['pokemons']), 0)

    def test_pagination(self):
        response = self.app.get('/pokemon/list', query_string={'search': ''})
        response2 = self.app.get('/pokemon/list', query_string={'search': '', 'page': 2})
        for pok2 in response2.json['pokemons']:
            self.assertGreater(pok2['id'], response.json['pokemons'][3]['id'])
        response3 = self.app.get('/pokemon/list', query_string={'search': '', 'page': -1})
        for pok1, pok3 in zip(response.json['pokemons'], response3.json['pokemons']):
            self.assertEqual(pok1['id'], pok3['id'])
        response4 = self.app.get('/pokemon/list', query_string={'search': '', 'page': response3.json['max_page']})
        response5 = self.app.get('/pokemon/list', query_string={'search': '', 'page': response3.json['max_page'] + 5})
        for pok4, pok5 in zip(response4.json['pokemons'], response5.json['pokemons']):
            self.assertEqual(pok4['id'], pok5['id'])

    def test_search(self):
        response = self.app.get('/pokemon/list', query_string={'search': 'bul'})
        for pok in response.json['pokemons']:
            self.assertIn('bul', pok['name'])

    def test_uniqueness(self):
        response = self.app.get('/pokemon/list')
        names = []
        for pok in response.json['pokemons']:
            names.append(pok['name'])
        self.assertCountEqual(names, set(names))


class TestPokemon(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_dif_names(self):
        response = self.app.get('/pokemon/1')
        response2 = self.app.get('/pokemon/2')
        self.assertNotEqual(response.json['name'], response2.json['name'])

    def test_all_stats(self):
        response = self.app.get('/pokemon/3')
        for stat in response.json:
            self.assertIsNotNone(stat)

    def test_unknown(self):
        response = self.app.get('/pokemon/09090909090')
        for stat in response.json:
            if stat != 'id':
                self.assertEqual(response.json[stat], 'unknown')


class TestRandomPokemon(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_really_random(self):
        trying = True
        count = 0
        while trying and count < 3:
            response = self.app.get('/pokemon/random')
            response2 = self.app.get('/pokemon/random')
            if response.json['id'] != response2.json['id']:
                trying = False
            count += 1
        self.assertTrue(not trying)


class TestFighting(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_stats(self):
        response = self.app.get('/fight', query_string={'user_id': 1, 'bot_id': 2})
        response2 = self.app.get('/fight', query_string={'user_id': 2, 'bot_id': 1})
        for stat1, stat2 in zip(response.json['player_poki'], response2.json['bot_poki']):
            self.assertEqual(response.json['player_poki'][stat1], response2.json['bot_poki'][stat2])
        for stat2, stat1 in zip(response2.json['player_poki'], response.json['bot_poki']):
            self.assertEqual(response2.json['player_poki'][stat2], response.json['bot_poki'][stat1])

    def test_values(self):
        response = self.app.get('/fight', query_string={'user_id': 3, 'bot_id': 4})
        self.assertTrue(response.json['player_poki']['attack'] > 0)
        self.assertTrue(response.json['player_poki']['hp'] > 0)
        self.assertTrue(response.json['bot_poki']['attack'] > 0)
        self.assertTrue(response.json['bot_poki']['hp'] > 0)


class TestAttack(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_without_fight(self):
        response = self.app.post('/fight/3')
        self.assertEqual(response.status_code, 404)

    def test_changes(self):
        response0 = self.app.get('/fight', query_string={'user_id': 3, 'bot_id': 4})
        response = self.app.post('/fight/3')
        self.assertEqual(response.status_code, 200)
        player_json = response.json['player_poki']
        bot_json = response.json['bot_poki']
        if player_json['val'] % 2 != bot_json['val'] % 2:
            self.assertEqual(player_json['hp'], response0.json['player_poki']['hp'] - bot_json['attack'])
        else:
            self.assertEqual(bot_json['hp'], response0.json['bot_poki']['hp'] - player_json['attack'])

    def test_db(self):
        q = sess.query(Fight).all()
        self.app.get('/fight', query_string={'user_id': 1, 'bot_id': 2})
        fighting = True
        while fighting:
            response = self.app.post('/fight/4')
            if response.json['player_poki']['hp'] <= 0 or response.json['bot_poki']['hp'] <= 0:
                fighting = False
                self.assertEqual(len(q) + 1, len(sess.query(Fight).all()))
                q = sess.query(Fight).order_by(Fight.id.desc()).first()
                self.assertEqual(q.player_id, response.json['player_poki']['id'])
                self.assertEqual(q.bot_id, response.json['bot_poki']['id'])
                self.assertEqual(q.rounds_count, len(response.json['rounds']))
                winner_id = q.bot_id if response.json['player_poki']['hp'] <= 0 else q.player_id
                self.assertEqual(q.winner_id, winner_id)


class TestFast(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_without_fight(self):
        response = self.app.get('/fight/fast')
        self.assertEqual(response.status_code, 404)

    def test_changes(self):
        response0 = self.app.get('/fight', query_string={'user_id': 3, 'bot_id': 4})
        response = self.app.get('/fight/fast')
        self.assertEqual(response.status_code, 200)
        player_damage = 0
        bot_damage = 0
        for round in response.json['rounds']:
            r = round.replace('vs', '')
            vals = r.split()
            if int(vals[0]) % 2 != int(vals[1]) % 2:
                player_damage += response.json['bot_poki']['attack']
            else:
                bot_damage += response.json['player_poki']['attack']
        self.assertEqual(response.json['player_poki']['hp'], response0.json['player_poki']['hp'] - player_damage)
        self.assertEqual(response.json['bot_poki']['hp'], response0.json['bot_poki']['hp'] - bot_damage)

    def test_db(self):
        q0 = sess.query(Fight).all()
        self.app.get('/fight', query_string={'user_id': 1, 'bot_id': 2})
        response = self.app.get('/fight/fast')
        q1 = sess.query(Fight).all()
        self.assertEqual(len(q0) + 1, len(q1))
        q = sess.query(Fight).order_by(Fight.id.desc()).first()
        self.assertEqual(q.player_id, response.json['player_poki']['id'])
        self.assertEqual(q.bot_id, response.json['bot_poki']['id'])
        self.assertEqual(q.rounds_count, len(response.json['rounds']))
        winner_id = q.bot_id if response.json['player_poki']['hp'] <= 0 else q.player_id
        self.assertEqual(q.winner_id, winner_id)


class TestSendMail(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_result(self):
        q = sess.query(Fight).order_by(Fight.id.desc()).first()
        response = self.app.post('/send_mail', data=json.dumps({"id": q.id, "email": EMAIL}),
                                 content_type="application/json")
        self.assertEqual(response.json['message'], "ОК")


class TestSaving(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_result(self):
        response = self.app.post('/save/1')
        self.assertEqual(response.json['message'], "OK")


class TestUI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        options = webdriver.ChromeOptions()
        service = Service(executable_path=binary_path)
        self.driver = webdriver.Chrome(service=service, options=options)

    def test_list(self):
        self.driver.get('http://192.168.2.46/')
        data = self.app.get('/pokemon/list', query_string={'search': '', 'page': 1}).json['pokemons']
        table = self.driver.find_element(By.XPATH, "//*[@class=\"myTable\"]")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertEqual(len(data), len(rows))
        for row, pok in zip(rows, data):
            cells = row.find_elements(By.TAG_NAME, "td")
            cell_text = cells[1].text.split('\n')
            self.assertEqual(cell_text[0], pok['name'])
            self.assertEqual(cell_text[2], f"Атака: {pok['attack']}")
            self.assertEqual(cell_text[3], f"Здоровье: {pok['hp']}")

    def test_pok_page(self):
        self.driver.get('http://192.168.2.46/')
        data = self.app.get('/pokemon/1').json
        self.driver.find_element(By.XPATH, "//*[@id=\"pok_name\"]").click()
        table = self.driver.find_element(By.XPATH, "//*[@class=\"myTable\"]")
        rows = table.find_elements(By.TAG_NAME, "tr")
        texts = []
        for row, stat in zip(rows, data):
            cells = row.find_elements(By.TAG_NAME, "td")
            texts.append(cells[1].text)
        self.assertEqual(texts[0], data['type'])
        self.assertEqual(int(texts[1]), data['attack'])
        self.assertEqual(int(texts[2]), data['hp'])
        self.assertEqual(int(texts[3]), data['height'])
        self.assertEqual(int(texts[4]), data['weight'])

    def test_search(self):
        self.driver.get('http://192.168.2.46/')
        search_input = self.driver.find_element(By.XPATH, "//*[@name=\"search\"]")
        search_input.send_keys("bul")
        self.driver.find_element(By.XPATH, "//*[@id=\"finder\"]").click()
        table = self.driver.find_element(By.XPATH, "//*[@class=\"myTable\"]")
        rows = table.find_elements(By.TAG_NAME, "tr")

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            cell_text = cells[1].text.split('\n')
            self.assertIn('bul', cell_text[0])

    def test_attack(self):
        self.driver.get('http://192.168.2.46/')
        self.driver.find_element(By.XPATH, "//*[@id=\"choice\"]").click()
        old_hp = self.driver.find_element(By.XPATH, "//*[@id=\"player_hp\"]").get_attribute("value")
        old_bot_hp = self.driver.find_element(By.XPATH, "//*[@id=\"bot_hp\"]").get_attribute("value")
        val_input = self.driver.find_element(By.XPATH, "//*[@id=\"number\"]")
        val_input.clear()
        val_input.send_keys(5)
        self.driver.find_element(By.XPATH, "//*[@id=\"attackk\"]").click()
        hp = self.driver.find_element(By.XPATH, "//*[@id=\"player_hp\"]").get_attribute("value")
        bot_hp = self.driver.find_element(By.XPATH, "//*[@id=\"bot_hp\"]").get_attribute("value")
        self.assertTrue(hp < old_hp or bot_hp < old_bot_hp)
