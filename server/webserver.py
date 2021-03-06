#!/usr/bin/python3.6
from flask import Flask, request, url_for, render_template, make_response, session, redirect, Markup
from database import session, UserSessions, Games, WhiteCards, BlackCards
from cookie_generator import generate_random_cookie
import json
import random
import copy
from startup import startup

app = Flask(__name__)
TEMPLATES_AUTO_RELOAD = True
mah_domain = "localhost"
game_max_score = 3

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

@app.route('/resetcookie')
def reset_cookie():
    res = make_response(redirect('/'))
    unique_cookie = generate_random_cookie()
    session.add(UserSessions(user_cookie=unique_cookie))
    session.commit()
    res.set_cookie("game_session", unique_cookie, max_age=60*60*24*365*2)
    return res

@app.route('/')
def index():
    cookie = request.cookies.get("game_session")
    print(cookie)
    if not cookie:
        res = make_response(render_template("homepage.html"))
        unique_cookie = generate_random_cookie()
        session.add(UserSessions(user_cookie=unique_cookie))
        session.commit()
        res.set_cookie("game_session", unique_cookie, max_age=60*60*24*365*2)
        return res
    else:
        print("User connected:", cookie)
        return render_template("homepage.html")


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
    raw_players.remove(user_object.id)
    for i in raw_players:
        player_names.append(session.query(UserSessions).filter_by(id =i).first().player_name)
    session.close()
    return render_template(
        "game_creator.html", 
        game_id = game_object.game_id, 
        players = player_names, 
        raw_players=raw_players,
        player_range = range(len(player_names)),
        admin = True,
        mah_domain = mah_domain
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
        game_object.turn_number = 1
        game_object.previous_winners = json.dumps({})
        #Choose turn order
        admin_id = (session.query(Games.admin).filter_by(admin=user_object.id).first()[0])
        players_turn_order = raw_players.copy()
        players_turn_order.append(admin_id)
        game_object.turn_order = json.dumps(players_turn_order)
        #Choose first player
        turn_selected_player = random.choice(players_turn_order)
        game_object.turn_selected_player = json.dumps(turn_selected_player)
        # Setup place for turn black cards, dict of all players except one going
        turn_white_cards = {}
        for tmp_player in players_turn_order:
            if tmp_player != turn_selected_player:
                turn_white_cards[tmp_player] = None
        game_object.turn_white_cards = json.dumps(turn_white_cards)
        # Divide up White cards
        ## TODO gotta rename some of this stuff
        played_black_cards = []
        player_hands = {}
        player_hand_size = 0
        for i in json.loads(game_object.players):
            player_hands[i] = [] 
            while player_hand_size != 7:
                total_black_cards = session.query(BlackCards).count()
                select_card = random.randint(0, total_black_cards - 1)
                if(select_card not in played_black_cards):
                    tmp_card = session.query(WhiteCards)[select_card].white_cards
                    played_black_cards.append(select_card)
                    player_hands[i].append(tmp_card)
                    player_hand_size += 1
            player_hand_size = 0
        game_object.white_cards_played = json.dumps(played_black_cards)
        game_object.players_hand = json.dumps(player_hands)
        #Select White Card
        total_black_cards = session.query(BlackCards).count()
        select_card = random.randint(0, total_black_cards - 1)
        tmp_card = session.query(BlackCards)[select_card].black_cards
        game_object.black_cards_played = json.dumps([select_card])
        game_object.players_white_card = json.dumps(tmp_card)
        game_object.turn_phase = "ReadWhiteCard"
        #Set players score
        tmp_players_score = {}
        for i in json.loads(game_object.players):
            tmp_players_score[i] = 0
            print(i)
        game_object.players_score = json.dumps(tmp_players_score)
        print(tmp_players_score)
        session.commit()
        return make_response(redirect('/game_id/' + game_object.game_id))
    else:
        print("ELSE IT IS")
        raw_players.remove(int(request.form["delete"]))
        game_object.players = json.dumps(raw_players)
        session.commit()
        return make_response(redirect('/play'))
        

@app.route('/game_id/<game_id>', methods=['GET'])
def play(game_id):
    cookie = request.cookies.get("game_session")
    user_object = session.query(UserSessions).filter_by(user_cookie=cookie).first()
    game_object = session.query(Games).filter_by(game_id=game_id).first()
    print("HASDASD", game_object.turn_phase)
    player_names = {}
    raw_players = json.loads(game_object.players)
    for i in raw_players:
        player_names[str(i)] = session.query(UserSessions).filter_by(id =i).first().player_name
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
            admin = False,
            mah_domain = mah_domain
        )
    elif game_object.turn_phase == "ReadWhiteCard" or game_object.turn_phase == "ChooseWhiteCard":
        #print(json.loads(game_object.players_hand))
        #print(len(json.loads(game_object.players_hand)))
        if user_object.id == json.loads(game_object.turn_selected_player):
            is_it_my_turn = True
        else:
            is_it_my_turn = False
        players_white_card = game_object.players_white_card
        #print(players_white_card)

        # Tell player to wait for other players to submit their white cards
        white_cards_in_played = json.loads(game_object.turn_white_cards)
        if str(user_object.id) in white_cards_in_played:
            if white_cards_in_played[str(user_object.id)] == None:
                slow_down = False
            else:
                slow_down = True
        else:
            slow_down = False

        # TODO Test if one can remove below three lines
        if type(players_white_card) == type("A"):
            print("We got an error of quotes in the JSON")
            players_white_card = game_object.players_white_card
        print((game_object.players_score))
        return render_template(
            "play.html", 
            players_turn = is_it_my_turn,
            turn_phase = game_object.turn_phase,
            user_id = str(user_object.id),
            game_id = game_object.game_id,
            player_names = player_names,
            players = json.loads(game_object.players),
            turn_number = game_object.turn_number,
            players_hand = json.loads(game_object.players_hand),
            players_white_card = players_white_card,
            players_score = json.loads(game_object.players_score),
            turn_selected_player = json.loads(game_object.turn_selected_player),
            is_it_my_turn = is_it_my_turn,
            turn_white_cards = json.loads(game_object.turn_white_cards),
            slow_down = slow_down
        )
    elif game_object.turn_phase == "DisplayWinner":
        return render_template(
            "game_winner.html", 
            MAH_WINNER = player_names[game_object.game_winner],
            turn_phase = game_object.turn_phase,
            user_id = str(user_object.id),
            game_id = game_object.game_id,
            player_names = player_names,
            players = json.loads(game_object.players),
            turn_number = game_object.turn_number,
            players_score = json.loads(game_object.players_score),
        )

@app.route('/game_id/<game_id>', methods=['POST'])
def get_user_game_input(game_id):
    cookie = request.cookies.get("game_session")
    user_object = session.query(UserSessions).filter_by(user_cookie=cookie).first()
    game_object = session.query(Games).filter_by(game_id=game_id).first()
    if request.form["turn_phase"] == "ReadWhiteCard":
        print(type(request.form))
        # Submit white card
        white_cards_in_played = json.loads(game_object.turn_white_cards)
        if white_cards_in_played[str(user_object.id)] == None:
            white_cards_in_played[str(user_object.id)] = request.form["black_card"]
            game_object.turn_white_cards = json.dumps(white_cards_in_played)
        else:
            return make_response(redirect('/game_id/' + game_id))
        # Remove white card from player
        all_player_hands = json.loads(game_object.players_hand)
        played_card_index = all_player_hands[str(user_object.id)].index(request.form["black_card"])
        del all_player_hands[str(user_object.id)][played_card_index]
        #all_player_hands[str(user_object.id)].remove(request.form["black_card"])
        
        # Draw new white card
        white_cards_played = json.loads(game_object.white_cards_played)
        not_already_picked = True
        while not_already_picked:
            print("WHILE HAPPENED")
            total_white_cards = session.query(BlackCards).count()
            select_card = random.randint(0, total_white_cards - 1)
            if(select_card not in white_cards_played):
                tmp_card = session.query(WhiteCards)[select_card].white_cards
                white_cards_played.append(select_card)
                not_already_picked = False
                # Put new white card in existing hand
                all_player_hands[str(user_object.id)].append(tmp_card)
        # Save new card drawn to cards played
        game_object.white_cards_played = json.dumps(white_cards_played)
        # Save white cards to database
        game_object.players_hand = json.dumps(all_player_hands)
        # Check if all players handed in cards
        count_responses = 0
        for i in white_cards_in_played.keys():
            if white_cards_in_played[i] != None:
                count_responses += 1
        if count_responses == len(json.loads(game_object.players)) - 1 :
            print("IF HAPPENS OVER HERE")
            game_object.turn_phase = "ChooseWhiteCard"
        # Save everything to database
        session.commit()
    elif request.form["turn_phase"] == "ChooseWhiteCard":
        # Check if correct player turn_selected_player
        if str(user_object.id) != game_object.turn_selected_player:
            return make_response(redirect('/game_id/' + game_id))
        # Find who sent in white card turn_white_cards
        all_white_cards = json.loads(game_object.turn_white_cards)
        for key in all_white_cards:
            if all_white_cards[key] == request.form["white_card_winner"]:
                winner = key
                print("WINNER IS " + str(winner))
                # Increment score of winning player
                all_players_score = json.loads(game_object.players_score)
                all_players_score[winner] = all_players_score[winner] + 1
                print(all_players_score)
                print("all_players_score[winner] = ", str(all_players_score[winner]))
                if all_players_score[winner] >= game_max_score:
                    print("Looks like we have a winner")
                    game_object.turn_phase = "DisplayWinner"
                    game_object.game_winner = winner
                game_object.players_score = json.dumps(all_players_score)
        # Set next player turn_selected_player
        turn_order = json.loads(game_object.turn_order)
        print("\n\n" + str(turn_order) + "\n\n")
        old_player = turn_order.index(json.loads(game_object.turn_selected_player))
        new_player = old_player + 1
        if new_player == len(turn_order):
            new_player = 0
        next_player_turn = turn_order[new_player]
        game_object.turn_selected_player = json.dumps(next_player_turn)
        # Reset turn_white_cards
        turn_white_cards = {}
        for tmp_player in turn_order:
            if tmp_player != next_player_turn:
                turn_white_cards[tmp_player] = None
        game_object.turn_white_cards = json.dumps(turn_white_cards)
        # Set next turn
        turn_num = game_object.turn_number
        turn_num += 1
        game_object.turn_number = turn_num
        # Save who won
        previous_winners = json.loads(game_object.previous_winners)
        previous_winners[turn_num-1] = {}
        previous_winners[turn_num-1]["Winner"] = winner
        previous_winners[turn_num-1]["whiteCard"] = request.form["white_card_winner"]
        previous_winners[turn_num-1]["blackCard"] = game_object.players_white_card
        # Reset game phase
        if game_object.turn_phase != "DisplayWinner":
            game_object.turn_phase = "ReadWhiteCard"
        game_object.previous_winners = json.dumps(previous_winners)
        # Save everything to database
        session.commit()
    return make_response(redirect('/game_id/' + game_id))

if __name__ == '__main__':
    startup()
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(use_reloader=True, debug=False, host= '0.0.0.0')
    # https://stackoverflow.com/questions/60539952/is-it-possible-to-change-code-of-flask-without-rerunning-the-flask-server-after
