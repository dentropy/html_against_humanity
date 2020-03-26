from flask import Flask, request, url_for, render_template, make_response, session, redirect
from database import session, UserSessions, Games
from cookie_generator import generate_random_cookie
import json

app = Flask(__name__)
#app.config['SECRET_KEY'] =  'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'

@app.route('/')
def index():
    cookie = request.cookies.get("game_session")
    print("User connected:", cookie)
    return render_template("homepage.html")

@app.route('/cookie')
def create_cookie():
    cookie = request.cookies.get("game_session")
    print(cookie)
    if not cookie:
        res = make_response(redirect('/'))
        unique_cookie = generate_random_cookie()
        session.add(UserSessions(user_cookie=unique_cookie))
        session.commit()
        res.set_cookie("game_session", unique_cookie, max_age=60*60*24*365*2)
        return res
    else:
        return make_response(redirect('/'))

@app.route("/choose_name", methods=['GET'])
def display_name():
    cookie = request.cookies.get("game_session")
    try:
        display_name = session.query(UserSessions).filter_by(user_cookie=cookie).first().player_name
        print(display_name)
    except:
        display_name = ""
        print("\n\nERROR Cookie likely missing from database\n\n")
    return render_template("choose_name.html" , display_name=display_name)

@app.route("/choose_name", methods=['POST'])
def update_display_name():
    cookie = request.cookies.get("game_session")
    data = request.form
    user = session.query(UserSessions).filter_by(user_cookie=cookie).first()
    user.player_name = data["display_name"]
    session.commit()
    user = session.query(UserSessions).filter_by(user_cookie=cookie).first()
    return render_template("choose_name.html" , display_name=user.player_name)

@app.route('/play', methods=['GET'])
def setup_game():
    cookie = request.cookies.get("game_session")
    user_object = session.query(UserSessions).filter_by(user_cookie=cookie).first()
    if session.query(Games).filter_by(admin=cookie).count() == 0 :
        print("NO IF")
        unique_room_id = generate_random_cookie(7)
        session.add( Games( admin = user_object.id, game_id = unique_room_id, players="[]") )
        session.commit()
    game_object = session.query(Games).filter_by(admin=user_object.id).first()
    player_names = []
    raw_players = json.loads(game_object.players)
    for i in raw_players:
        player_names.append(session.query(UserSessions).filter_by(id =i).first().player_name)
    session.close()
    return render_template(
        "game_creator.html", 
        game_id = game_object.game_id, 
        players = player_names, 
        raw_players=raw_players,
        player_range = range(len(raw_players)),
        admin = True
    )

@app.route('/play/', methods=['POST'])
def set_initial_game_state():
    cookie = request.cookies.get("game_session")
    user_object = session.query(UserSessions).filter_by(user_cookie=cookie).first()
    game_object = session.query(Games).filter_by(admin=user_object.id).first()
    raw_players = json.loads(game_object.players)
    if request.form["delete"] == "start":
        game_object.game_started = True
        session.commit()
        return "Game Start"
    else:
        raw_players.remove(int(request.form["delete"]))
        game_object.players = json.dumps(raw_players)
        session.commit()
        return make_response(redirect('/play'))
        

@app.route('/game_id/<game_id>')
def play(game_id):
    cookie = request.cookies.get("game_session")
    user_object = session.query(UserSessions).filter_by(user_cookie=cookie).first()
    game_object = session.query(Games).filter_by(game_id=game_id).first()
    if game_object.game_started == False:
        if game_object.players == None or game_object.players == "null":
            game_object.players = json.dumps([user_object.id])
        elif str(user_object.id) not in json.dumps(game_object.players):
            old_entry = json.loads(game_object.players)
            old_entry.append(user_object.id)
            game_object.players = json.dumps(old_entry)
        session.commit()
        game_object = session.query(Games).filter_by(game_id=game_id).first()
        player_names = []
        for i in json.loads(game_object.players):
            player_names.append(session.query(UserSessions).filter_by(id =i).first().player_name)
        session.close()
        return render_template(
            "game_creator.html", 
            game_id = game_object.game_id,
            players = player_names, 
            admin = False
        )
    else:
        return "work in process"

if __name__ == '__main__':
    app.run()
