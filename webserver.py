from flask import Flask, request, url_for, render_template, make_response, session, redirect
from database import session, UserSessions, Games, WhiteCards, BlackCards
from cookie_generator import generate_random_cookie
import json
import random
import copy

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
        session.add( Games( admin = user_object.id, game_id = unique_room_id, players=json.dumps([user_object.id]), game_started=False) )
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
        print("IT IS IF")
        game_object.game_started = True
        #Divide up black cards
        played_black_cards = []
        player_hands = {}
        player_hand = 0
        for i in game_object.players:
            player_hands[i] = [] 
            while player_hand != 7:
                total_black_cards = session.query(BlackCards).count()
                select_card = random.randint(0, total_black_cards - 1)
                if(select_card not in played_black_cards):
                    tmp_card = session.query(WhiteCards)[select_card].white_cards
                    played_black_cards.append(select_card)
                    player_hands[i].append(tmp_card)
                    player_hand += 1
        game_object.black_cards_played = json.dumps(played_black_cards)
        game_object.player_hand = player_hands
        #Choose turn order
        admin_id = (session.query(Games.admin).filter_by(admin=user_object.id).first()[0])
        players_turn_order = raw_players.copy()
        players_turn_order.append(admin_id)
        game_object.turn_order = json.dumps(players_turn_order)
        #Choose first player
        turn_selected_player = random.choice(players_turn_order)
        game_object.turn_selected_player = json.dumps(turn_selected_player)
        #Select White Card
        total_black_cards = session.query(BlackCards).count()
        select_card = random.randint(0, total_black_cards - 1)
        tmp_card = session.query(BlackCards)[select_card].black_cards
        game_object.black_cards_played = json.dumps([select_card])
        game_object.players_white_card = tmp_card
        game_object.turn_phase = "ReadWhiteCard"
        # Setup place for turn black cards
        turn_black_cards = {}
        for tmp_player in game_object.players:
            if tmp_player != turn_selected_player:
                turn_black_cards[tmp_player] = None
        game_object.turn_black_cards = json.dumps(turn_black_cards)
        session.commit()
        return make_response(redirect('/game_id/' + game_object.game_id))
    else:
        print("ELSE IT IS")
        raw_players.remove(int(request.form["delete"]))
        game_object.players = json.dumps(raw_players)
        session.commit()
        return make_response(redirect('/play'))
        

@app.route('/game_id/<game_id>')
def play(game_id):
    cookie = request.cookies.get("game_session")
    user_object = session.query(UserSessions).filter_by(user_cookie=cookie).first()
    game_object = session.query(Games).filter_by(game_id=game_id).first()
    player_names = []
    raw_players = json.loads(game_object.players)
    for i in raw_players:
        player_names.append(session.query(UserSessions).filter_by(id =i).first().player_name)
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
    elif game_object.turn_phase == "ReadWhiteCard" and user_object.id == game_object.turn_selected_player:
        return render_template(
            "play.html", 
            turn_phase = game_object.turn_phase,
            user_id = user_object.id,
            game_id = game_object.game_id,
            player_names = player_names,
            players = json.dumps(game_object.players),
            turn_number = game_object.turn_number,
            players_hand = json.dumps(game_object.players_hand),
            players_white_card = game_object.players_white_card,
            players_score = game_object.players_score,
            turn_selected_player = game_object.turn_selected_player,
            turn_black_cards = game_object.turn_black_cards
        )
    elif game_object.turn_phase == "ReadWhiteCard" and user_object.id != game_object.turn_selected_player:
        return render_template(
            "play.html", 
            players = game_object.players,
            turn_number = game_object.turn_number,
            players_hand = game_object.players_hand,
            players_white_card = game_object.players_white_card,
            players_score = game_object.players_score,
            turn_selected_player = game_object.turn_selected_player,
            turn_black_cards = game_object.turn_black_cards
        )
    elif game_object.turn_phase == "ChooseBlackCard" and user_object.id == game_object.turn_selected_player:
        return "work in progress"
    elif game_object.turn_phase == "ChooseBlackCard" and user_object.id != game_object.turn_selected_player:
        return "work in progress"
    elif game_object.turn_phase == "DisplayWinner":
        return "work in progress"

if __name__ == '__main__':
    app.run()
