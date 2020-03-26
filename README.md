# Implementation web based Cards Against Humanity in Python

* TODO
  * [✓] Write HTML for homepage
  * [✓] Implement session cookies
  * [✓] Store session cookies in database
  * [✓] Import Cards Against Humanity Questions JSON from github into database
  * [ ] Pseudocode Game Logic
  * [ ] Write user stories

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
