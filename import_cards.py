#!/usr/bin/python3.6
import urllib.request
import json
from database import session, WhiteCards, BlackCards
import os.path
if os.path.isfile("cah.json"):
    print("Found file for Cards")
    with open('cah.json', 'r') as f:
        cards = json.load(f)
else:
    print("Fetching cards from interwebs")
    cards_url = "https://raw.githubusercontent.com/crhallberg/json-against-humanity/master/dev/cah.json"
    cards_url_response = urllib.request.urlopen(cards_url)
    cards = json.loads(cards_url_response.read())
number_of_cards = session.query(WhiteCards.white_cards).count()
if number_of_cards == 0:
    string_type = type("S")
    for i in cards["blackCards"]:
        if type(i) != string_type:
            session.add( BlackCards( black_cards = str(i["text"]), num_white_cards = int(i["pick"]) ) )
        else:
            session.add( BlackCards( white_cards = str(i),num_white_cards = 1 ))
        print(i)
    for i in cards["whiteCards"]:
        print(i)
        session.add( WhiteCards( white_cards = str(i)))

    session.commit()
    print("Successfully imported cards")
else:
    print("Looks like you already have %d cards in database" % number_of_cards)
    print("No new cards have be input at this time")