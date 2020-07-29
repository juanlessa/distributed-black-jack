import argparse
import redis
import socket
import selectors
import hashlib
import time
from utils import score

#redis connect
def redis_connect():
    table = redis.Redis('localhost')
    return table
##########################################################################################

#acept connection
def accept(sock, mask, self_name):
    conn, addr = sock.accept()  # Should be ready
    conn.setblocking(False)
    #receiving connection port
    addr = conn.recv(128).decode('utf-8')
    conn.send(f"{self_name}".encode('utf-8'))
    addr = str(addr).split(":")
    conn.close()
    return [str(addr[1]), int(addr[0])]
##########################################################################################

def get_card():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('localhost', 5000))
    except:
        data = "U"
    else:
        s.send(f"GC".encode('utf-8'))
        data = s.recv(2).decode('utf-8')
    s.close()
    return str(data).strip()
##########################################################################################

def get_hash():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('localhost', 5000))
    except:
        data = "U"
    else:
        s.send(f"HC".encode('utf-8'))
        data = s.recv(35).decode('utf-8')
    s.close()
    return data
##########################################################################################

def inform_players(message, players_connection):
    for n, port in players_connection:
        if n == "I":
            continue
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('localhost', port))
        except:
            print(f"[*] error connecting player {n} on port {port}")
        else:
            s.send(f"{message}".encode('utf-8'))
        s.close()
##########################################################################################

def receive_move(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    conn.setblocking(False)
    data = ""
    while data == "":
        try:
            data = conn.recv(1).decode('utf-8')
        except:
            data = ""
    conn.close()
    return data
##########################################################################################

#main
def main(self_port, players_ports):
    #important names
    need_connect = list(args.players)   #players not connected yet
    players_connection = []             #players already connected
    self_cards = []                     #my cards
    current_score = 0                   #my score
    players_moves = []                  #players movements
    playing = list(need_connect)        #players not defeat
    playing.append(self_port)
    playing = list(sorted(playing))

    #player name
    self_name = ""
    while self_name == "":
        self_name = input("what your name? ")

    #try connect with others
    aux = list(need_connect)
    for i in range(len(need_connect)):
        players_connection.append(['dont know', need_connect[i]])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('localhost', need_connect[i]))
        except:
            s.close()
        else:
            s.send(f"{self_port}:{self_name}".encode('utf-8'))
            players_connection[i][0] = s.recv(128).decode('utf-8')
            aux.remove(need_connect[i])
            print(f"\033[32m[*] now {players_connection[i][0]} is connected on port {players_connection[i][1]}\033[m")
            s.close()
    need_connect = list(aux)

    #create socket
    sock = socket.socket() #socket to receive connections
    sock.bind(('localhost', self_port))
    sock.listen(100)
    sock.setblocking(False)

    #create selector
    selector = selectors.DefaultSelector()

    #register event - acept
    selector.register(sock, selectors.EVENT_READ, accept)

    #waitng other players
    while len(need_connect) != 0:
        print(f'\033[33m[*] waiting {len(need_connect)} players connect on port {need_connect}\033[m')
        events = selector.select()
        for key, mask in events:
            callback = key.data
            result = callback(key.fileobj, mask, self_name)
            for i in range(len(players_connection)):
                if players_connection[i][1] == result[1]:
                    players_connection[i] = result
                    break
            print(f"\033[32m[*] now {result[0]} is connected on port {result[1]}\033[m")
            need_connect.remove(result[1])
    print("\033[33m[*] all players are connected\033[m")
    #acrecent me in players_connection
    players_connection.append(["I", self_port])
    #sort player_connection
    players_connection = sorted(players_connection, key = lambda porta: porta[1])
    #selector unregister
    selector.unregister(sock)

    time.sleep(0.5)
    #blackjack
    print("\n")
    print("\t┏━━┓ ┏┓         ┏┓      ┏┓        ┏┓   ")
    print("\t┃┏┓┃ ┃┃         ┃┃      ┃┃        ┃┃   ")
    print("\t┃┗┛┗┓┃┃ ┏━━┓┏━━┓┃┃┏┓    ┃┃┏━━┓┏━━┓┃┃┏┓ ")
    print("\t┃┏━┓┃┃┃ ┃┏┓┃┃┏━┛┃┗┛┛  ┏┓┃┃┃┏┓┃┃┏━┛┃┗┛┛ ")
    print("\t┃┗━┛┃┃┗┓┃┏┓┃┃┗━┓┃┏┓┓  ┃┗┛┃┃┏┓┃┃┗━┓┃┏┓┓ ")
    print("\t┗━━━┛┗━┛┗┛┗┛┗━━┛┗┛┗┛  ┗━━┛┗┛┗┛┗━━┛┗┛┗┛ ")
    print("\n")

    #seletor register connections
    selector.register(sock, selectors.EVENT_READ, receive_move)
    
    initial_round = True
    current_player = 0
    last_card = ""
    #game
    while True:
        #when has only one player
        if len(playing) == 1:
            break
        #skip players who already lost
        if players_connection[current_player][1] in playing:
            #my turn to play  
            if players_connection[current_player][1] == self_port:
                #ask to cards from deck
                if initial_round:   #initial round
                    c = get_card()
                    if c == "U":
                        inform_players("U", players_connection)
                        print(f"\033[31m[*] deck.py is not active now\033[m")
                        selector.unregister(sock)
                        selector.close()
                        sock.close()
                        exit(1)
                    self_cards.append(c)
                    c = get_card()
                    if c == "U":
                        inform_players("U", players_connection)
                        print(f"\033[31m[*] deck.py is not active now\033[m")
                        selector.unregister(sock)
                        selector.close()
                        sock.close()
                        exit(1)
                    self_cards.append(c)
                    current_score = score(self_cards)
                    initial_round = False
                if last_card == 1:
                    last_card = get_card()
                    if last_card == "U":
                        inform_players("U", players_connection)
                        print(f"\033[31m[*] deck.py is not active now\033[m")
                        selector.unregister(sock)
                        selector.close()
                        sock.close()
                        exit(1)
                #get my move
                if last_card != "":
                    self_cards.append(last_card)
                    current_score = score(self_cards)
                #my score
                print(f"Current score: {current_score}")
                jogada = interact_with_user1(self_cards)
                players_moves.append([current_player, jogada])
                if jogada == "H":           #ask a card
                    last_card = 1
                    inform_players("H", players_connection)     #"H" == hit
                    print("\033[33m[*] wait othors playars\033[m")
                elif jogada == "S" :        #stand
                    last_card = ""
                    inform_players("S", players_connection)     #"S" == stand
                    print("\033[33m[*] wait othors playars\033[m")
                elif jogada == "W":         #Win
                    inform_players("W", players_connection)     #"W" == win
                    print("\033[33m[*] you said you win\033[m")
                    break
                elif jogada == "D":            #Defeat
                    inform_players("D", players_connection)     #"D" == Defeat
                    playing.remove(self_port)
                    print("\033[31m[*] you defeat\033[m")
            #not my turn
            else:
                #waiting other player move
                while True:
                    events = selector.select()
                    for key, mask in events:
                        callback = key.data
                        jogada = callback(key.fileobj, mask)    #receive move
                        break
                    break
                players_moves.append([current_player, jogada])
                #analysing move
                if jogada == "H":           #"hit"
                    print(f"\033[33m[*] {players_connection[current_player][0]} hit\033[m")
                elif jogada == "S":           #"stand"
                    print(f"\033[33m[*] {players_connection[current_player][0]} stand\033[m")
                elif jogada == "W":         #"win"
                    print(f"[*] {players_connection[current_player][0]} said he win\033[m")
                    break
                elif jogada == "D":         #"Defeat"
                    print(f"\033[31m[*] {players_connection[current_player][0]} defeat\033[m")
                    playing.remove(players_connection[current_player][1])
                else:                       #deck.py not active
                    print(f"\033[31m[*] deck.py is not active now\033[m")
                    selector.unregister(sock)
                    selector.close()
                    sock.close()
                    exit(1)
        #determine next player
        if current_player < len(players_connection)-1:
            current_player += 1
        else:
            current_player = 0
    
    #put my cards on table (redis)
    for n, port in players_connection:
        if port == self_port:
            time.sleep(0.2)
            table = redis_connect()
            table.delete(str(self_port))
            for c in self_cards:
                table.rpush(str(self_port), str(c))
            inform_players("O", players_connection) #"O" == OK
        else:
            #waiting other player save his cards on table
            while True:
                events = selector.select()
                for key, mask in events:
                    callback = key.data
                    jogada = callback(key.fileobj, mask)    #receive ok
                    break
                break

    players_score = [] #score and cards from others players
    
    #get players cards
    for n, port in players_connection:
        if port == self_port:
            players_score.append([port, current_score, self_cards])
        else:
            cards = table.lrange(str(port), 0, -1)
            for i in range(len(cards)):
                cards[i] = cards[i].decode("utf-8")
            players_score.append([port, score(cards), cards])
    
    #close client redis
    table.close()

    #determine winner
    winner = 0
    for port, sc, c in players_score:
        if sc == 21:
            winner = port
            break
        elif (21 > sc) and (sc > winner):
            winner = port
    #get winner name
    for n, port in players_connection:
        if port == winner:
            winner = n
            break
    print(f"\033[33m[*] {winner} Won\033[m")
    exit
    #md5sum 
    #last but one player and last player
    if (self_port == players_connection[-2][1]) or (self_port == players_connection[-1][1]):
        #deck correct hash
        deck_hash = get_hash()
        #sequence of played cards
        played_cards = []
        initial_round = True
        next_move = []
        for i in range(len(players_connection)):
            next_move.append(0)
        for player, j in players_moves:
            if initial_round:
                played_cards.append(players_score[player][2].pop(0))
                played_cards.append(players_score[player][2].pop(0))
            if next_move[player] == 1:
                played_cards.append(players_score[player][2].pop(0))
            if (j == "H") and len(players_score[player][2]) != 0:
                next_move[player] = 1
            if (player == len(players_score)-1) and initial_round:
                initial_round = False
        #calculate hash code
        print(played_cards)
        played_hash = hashlib.md5(f'{played_cards}'.encode('utf-8')).hexdigest()
        print(played_hash)
        print(deck_hash)
        if str(deck_hash).strip() == str(played_hash).strip():
            inform_players("O", players_connection[0:-2])
        else:
            inform_players("C", players_connection[0:-2])
    #other players
    else:
        while True:
            events = selector.select()
            for key, mask in events:
                callback = key.data
                played_hash1 = callback(key.fileobj, mask)
                break
            break

        while True:
            events = selector.select()
            for key, mask in events:
                callback = key.data
                played_hash2 = callback(key.fileobj, mask)    #receive ok
                break
            break

    #validation
    #lat player and last but one player
    if (self_port == players_connection[-1][1]) or (self_port == players_connection[-2][1]):
        if str(deck_hash).strip() == str(played_hash).strip():
            print('\033[32m[*] there was no cheating\033[m')
        else:
            print("\033[31m[*] there was cheating\033[m")
    #other players
    else:
        if played_hash1 == "O" and played_hash2 == "O":
            print('\033[32m[*] there was no cheating\033[m')
        else:
            print("\033[31m[*] there was cheating\033[m")
    
    #close
    selector.unregister(sock)
    selector.close()
    sock.close()
##########################################################################################

#interactive painel
def interact_with_user1(cards):
    """ All interaction with user must be done through this method.
    YOU CANNOT CHANGE THIS METHOD. """

    print(f"Current cards: {cards}")
    print("(H)it")
    print("(S)tand")
    print("(W)in")  # Claim victory
    print("(D)efeat") # Fold in defeat
    key = " "
    while key not in "HSWD":
        key = input("> ").upper()
    return key.upper()
##########################################################################################

def singleplayer():

    time.sleep(0.5)

    #blackjack
    print("\n")
    print("\t┏━━┓ ┏┓         ┏┓      ┏┓        ┏┓   ")
    print("\t┃┏┓┃ ┃┃         ┃┃      ┃┃        ┃┃   ")
    print("\t┃┗┛┗┓┃┃ ┏━━┓┏━━┓┃┃┏┓    ┃┃┏━━┓┏━━┓┃┃┏┓ ")
    print("\t┃┏━┓┃┃┃ ┃┏┓┃┃┏━┛┃┗┛┛  ┏┓┃┃┃┏┓┃┃┏━┛┃┗┛┛ ")
    print("\t┃┗━┛┃┃┗┓┃┏┓┃┃┗━┓┃┏┓┓  ┃┗┛┃┃┏┓┃┃┗━┓┃┏┓┓ ")
    print("\t┗━━━┛┗━┛┗┛┗┛┗━━┛┗┛┗┛  ┗━━┛┗┛┗┛┗━━┛┗┛┗┛ ")
    print("\n")

    players_moves = []
    self_cards = []
    initial_round = True
    last_card = ""
    while True:
        #ask to cards from deck
        if initial_round:   #initial round
            c = get_card()
            if c == "U":
                print(f"\033[31m[*] deck.py is not active now\033[m")
                exit(1)
            self_cards.append(c)
            c = get_card()
            if c == "U":
                print(f"\033[31m[*] deck.py is not active now\033[m")
                exit(1)
            self_cards.append(c)
            current_score = score(self_cards)
            initial_round = False 
        if last_card != "":
            self_cards.append(last_card)
            current_score = score(self_cards)
        #my score
        print(f"Current score: {current_score}")
        #get my move
        jogada = interact_with_user1(self_cards)
        players_moves.append(jogada)
        if jogada == "H":           #ask a card
            last_card = get_card()
            if last_card == "U":
                print(f"\033[31m[*] deck.py is not active now\033[m")
                exit(1)
        elif jogada == "S" :        #stand
            last_card = ""
        elif jogada == "W":         #Win
            print("\033[33m[*] you win\033[m")
            break
        elif jogada == "D":            #Defeat
            print("\033[31m[*] you defeat\033[m")
            break
    
    #md5
    #deck correct hash
    deck_hash = get_hash()
    played_hash = hashlib.md5(f'{self_cards}'.encode('utf-8')).hexdigest()
    if str(deck_hash).strip() == str(played_hash).strip():
        print('\033[32m[*] there was no cheating\033[m')
    else:
        print("\033[31m[*] there was cheating\033[m")
##########################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--self', required=True, type=int)
    parser.add_argument('-p', '--players', nargs='+', type=int)
    args = parser.parse_args()
    
    #singleplayer
    if not args.players:
        singleplayer()
        exit()

    if args.self in args.players:
        print(f"{args.self} must not be part of the list of players")
        exit(1) 

    #main
    main(args.self, args.players)
 