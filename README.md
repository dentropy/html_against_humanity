# Implementation web based Cards Against Humanity in Python

## Install Instructions

``` bash
pip3 install sqlalchemy
pip3 install flask
python3 webserver.py
```

* TODO
  * [✓] Write HTML for homepage
  * [✓] Implement session cookies
  * [✓] Store session cookies in database
  * [✓] Import Cards Against Humanity Questions JSON from github into database
  * [✓] Generalized Pseudocode Game Logic
  * [✓] Write user stories
  * [✓] List number of html templates are required
  * [✓] Generate html templates
  * [✓] Map out database game logic and update schema
  * [✓] Document site map of which route does what
  * [✓] Write code so users can choose a display name
  * [✓] Write code so user can create room and invite other players
    * [✓] Generate and display join link
    * [✓] Allow others to join a room
    * [✓] Let admin remove players that have joined their room
  * [✓] Setup Initial Game State
    * [✓] Distribute White cards
    * [✓] Choose turn order
    * [✓] Choose first player
    * [✓] Select first white card
  * [✓] Separate white cards by number of black cards they require
    * [✓] Write code import form json file rather than web
  * [✓] Restart server when files are changed
  * [✓] Automatically add cookie if user does not have one
  * [✓] Have API end point to generate new cookie
  * [✓] List what data in database has to turn for each phase of turn
  * [✓] Map out turn phase
  * [✓] Map out master turn html template
  * [✓] Write turn logic
  * [✓] Webserver automatically fetch json against humanity
  * [✓] Delete unused HTML files
  * [✓] Do not show admin as able to kick themselves from their own game
  * [✓] Show player names rather than ID's in game lobby
  * [✓] After player send in card tell them they have to wait
  * [ ] Show home page on every page
  * [✓] Inject javascript that refreshes page
  * [✓] Have variable for server IP/dns name
  * [✓] Display user score
  * [✓] When player choosing white card, take out debugging information
  * [✓] Test end game condition

## Game logic Pseudocode

* Cards are distributed
  * Seven black cards each
* From group of people select a player to go first at random
  * Selected player selects a white card
  * White card is displayed / read aloud to all player playing
  * All players select one of their black cards
  * After all black cards submitted selected player chooses one black card
  * Selected player's selected black card is displayed / read aloud to other players
  * Player that submitted selected black card to selected player score increased by one
  * Game finishes when a specified score is selected

## User Story

Abby, John, and Sarah are want to play cards against humanity online.
Abby goes to a website and creates a room to play with her friends.
After generating a room abby can either share a room id or URL with her friends in order to play
Once abby can see all her friends in the room she can start the game

Sarah goes first and the web page displays the white card and is told to wait because she goes first
Abby and John see the white card and their hand and are told to choose one of their black cards

John sends cards in first and everyone's user interface updates to display this fact

Abby submits her card and the game moves to next phase

Sarah is displayed the two black cards that were submitted

Sarah chooses a black card she thinks fits best given the white card she played earlier

Sarah choose Abby's card therefore abby now holds that white card and score is increased by one

John's turn is next and a white card is selected for his turn and displayed to the room

## HTML Templates Required

* Homepage - homepage.html
* Game Creator / Manager - game_creator.html
* Users Turn Pages
  * Read white card and wait for other players to choose black cards
    * read_white_card.html
  * Display and choose black card
    * choose_other_player_black_card.html
* Not Users Turn Pages
  * Select a black card
    * choose_black_card.html
  * Wait for user to choose black card
    * wait_for_round_winner.html
* Turn winner page - turn_winner.html
* Game winner page - game_winner.html
* Choose name - choose_name.html

## Schema and game logic

* Games have to be stored in a row
* Store entire game state on a row or manage evolving game state?
  * Entire game state will be in memory somewhere so it is easier to have entire game state in a row for now
* How to track users?
  * Each cookie is a user for now, login will come later

## Data that needs to be stored in database

* Still looking for new players - game_started
* Player data
  * Player's Name - UserSessions.player_name
  * Players Hand - players_hand
  * Players score - players_score
  * White cards player has acquired - players_white_card
* Game data
  * White cards played in game so far - white_cards_played
  * Black cards given out to players so far - black_cards_played
  * Game phase
    * Selected payer - turn_selected_player
    * White Card currently in play - turn_white_card
    * Who submitted black cards - turn_black_cards
    * Who chooses cards and when = turn_phase
  * Turn order - turn_order

## Site map

* ```/```
  * Home page
* ```/choose_name```
  * Change / Select display name
* ```/play```
  * Create and manage a room
* ```/game_id/<game_id>```
  * Generate HTML depending on what phase and whose turn it is

## Brainstorming

* Is is possible to play the game from a single HTML page?
  * It is possible but is it optimal for design
  * The game basically has four states therefore if statements can manage a lot of the logic
  * All game state data flows to page making things easier
  * What pages would this single page replace?
    * read_white_card.html
    * choose_other_player_black_card.html
    * choose_black_card.html
    * wait_for_round_winner.html
    * turn_winner.html

## Map out turn phase

There are four phases to a turn on CAH

1. "ReadWhiteCard" Select white card and display it while allowing users to select black cards

   * Submit White Card
     * row: turn_white_cards
   * Remove white card from player hand
     * row: players_hand
   * Draw new white card
     * row: white_cards and white_cards_played
   * Put new white card in existing hand
     * players_hand
   * Check if all players handed in cards
     * turn_white_cards, turn_phase and players
  
   * Data Required:
      * turn_white_cards
      * white_cards_played
      * white_cards
      * players_hand
      * turn_phase

2. "ChooseWhiteCard" All players have selected black cards, they are shuffled and user selects winning card

   * Data Required:
      * turn_selected_player
      * turn_white_cards
      * Players
      * turn_phase
      * turn_order
  
   * Display all cards to who's turn it is and have them choose one

3. "DisplayWinner" Winner of round is displayed

   * Data Required:
      * turn_selected_player
      * turn_white_cards
      * turn_phase
      * turn_number
      * white_cards_played

## Bugs

* Some parts of game state should lock after game starts
* Limit number of white cards to be played
* Only allowed to play one white card
* White cards move around on user
* Should not be able to remove oneself from game
* Games work with one or two players
* If cookie not in database there are a lot of errors
* Players represented multiple times in turn order

## Links

* [Use HTML Template](https://stackoverflow.com/questions/3206344/passing-html-to-template-using-flask-jinja2)
