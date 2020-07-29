# Distributed BlackJack
### This is a BlackJack game that I developed for the distributed computing class

## how to play?
 This game was configured to be played in localhost  
 So to play you need:  
* One terminal to be de deck of cards  
##### $ python3 deck.py  
 *  Tow or more terminal to be the players  
##### $ python3 player.py -s 1100 -p 1200 1300 1400  
##### $ python3 player.py -s 1200 -p 1100 1300 1400  
##### $ python3 player.py -s 1300 -p 1100 1200 1400  
##### $ python3 player.py -s 1400 -p 1100 1200 1300    
  -s or --self is your port  
-p or --players are the other players ports    
[! [vídeo de demonstração do jogo] (http://img.youtube.com/vi/1x4Q0_yfiO8/0.jpg)] (http://www.youtube.com/watch?v=1x4Q0_yfiO8 "Black Jack distribuído - exemplo 1 ")

    
 * You can use one or more bad_player.py to be able to cheating in game  
##### $ python3 player.py -s 1100 -p 1200 1300 1400  
##### $ python3 player.py -s 1200 -p 1100 1300 1400  
##### $ python3 player.py -s 1300 -p 1100 1200 1400  
##### $ python3 bad_player.py -s 1400 -p 1100 1200 1300  
