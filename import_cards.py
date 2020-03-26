import urllib.request
import json
from database import session, WhiteCards, BlackCards
cards_url = "https://raw.githubusercontent.com/crhallberg/json-against-humanity/master/dev/cah.json"
cards_url_response = urllib.request.urlopen(cards_url)
cards = json.loads(cards_url_response.read())
number_of_cards = session.query(WhiteCards.white_cards).count()
if number_of_cards == 0:
    for i in cards["blackCards"]:
        session.add( BlackCards( black_cards = str(i) ) )
        print(i)
    for i in cards["whiteCards"]:
        session.add( WhiteCards( white_cards = str(i) ) )
        print(i)
    session.commit()
    print("Successfully imported cards")
else:
    print("Looks like you already have %d cards in database" % number_of_cards)
    print("No new cards have be input at this time")