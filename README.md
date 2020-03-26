# Implementation web based Cards Against Humanity in Python

* TODO
  * [✓] Write HTML for homepage
  * [✓] Implement session cookies
  * [✓] Store session cookies in database
  * [✓] Import Cards Against Humanity Questions JSON from github into database
  * [✓] Pseudocode Game Logic
  * [✓] Write user stories
  * [✓] List number of html templates are required
  * [✓] Generate html templates
  * [ ] Map out database game logic and update schema
  * [ ] Document site map of which route does what

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

## Data that needs to be stored in database

* Player data
  * Player's Name
  * Players Hand
  * Players score
  * White cards player has acquired
* Game data
  * White cards played in game so far
  * Black cards given out to players so far
  * Game phase
    * Selected payer
    * White Card currently in play
    * Who submitted black cards
    * Black cards submitted
    * Who submitted which black card

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

## Design decisions

* How are games stored, a row or a table?
* How to track users?

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
