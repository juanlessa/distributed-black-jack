# Distributed BlackJack
### This is a BlackJack game that I developed for the distributed computing class

## how to play?
 This game was configured to be played in localhost  
 So to play you need:  
* One terminal to be the deck of cards  
##### $ python3 deck.py  
 * Two or more terminal to be the players  
##### $ python3 player.py -s 1100 -p 1200 1300 1400  
##### $ python3 player.py -s 1200 -p 1100 1300 1400  
##### $ python3 player.py -s 1300 -p 1100 1200 1400  
##### $ python3 player.py -s 1400 -p 1100 1200 1300    
  -s or --self is your port  
-p or --players are the other players ports    
  
  #### This video is a quick demonstration of game
[![ this is the video demonstrating a game match](http://img.youtube.com/vi/a7zL75LsvI0/0.jpg)](http://www.youtube.com/watch?v=a7zL75LsvI0 "Distributed Black Jack - Game Demonstration")

    
 * You can use one or more bad_player.py to be able to cheating in game  
##### $ python3 player.py -s 1100 -p 1200 1300 1400  
##### $ python3 player.py -s 1200 -p 1100 1300 1400  
##### $ python3 player.py -s 1300 -p 1100 1200 1400  
##### $ python3 bad_player.py -s 1400 -p 1100 1200 1300  
