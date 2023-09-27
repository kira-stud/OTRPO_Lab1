from flask import Flask, render_template
import pokebase as pb

app = Flask(__name__)

@app.route("/")
@app.route("/<search>")
def index(search=""):
    pokies0 = pb.APIResourceList('pokemon')
    pokies = []
    for p in pokies0:
        if search in p['name']:
            pokies.append(p)
    print(len(pokies))
    return render_template("pokies.html", poki=pokies)


if __name__ == "__main__":
    app.run(debug=True)

