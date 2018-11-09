import socket
import pickle
import random
import time
from helpers import *

## Bob

def Main():
    ## Alice's server for initial reshuffling
    host_alice = '127.0.0.1'
    port_alice = 5006
    client_alice = socket.socket()
    client_alice.connect((host_alice, port_alice))

    print("Connected to Alice.\n")

    print("Receive all cards from Alice encrypted")
    ## REceive all cards from Alice encrypted
    shuffled_deck_alice = client_alice.recv(4096)
    shuffled_deck_alice = pickle.loads(shuffled_deck_alice)

    ## Shuffle for random draws
    print("Shuffling")
    random.shuffle(shuffled_deck_alice)

    ## Alice takes first 5 cards, Bob takes last 5
    alice_cards = shuffled_deck_alice[0:5]
    alice_cards = pickle.dumps(alice_cards, -1)

    ## Send ALice's cards to Alice
    print("Sending Alice's cards...")
    client_alice.sendall(alice_cards)
    print("Deck sent back to Alice.\n")

    num_cards = len(shuffled_deck_alice)
    bob_key = 2
    print("A deck of ", num_cards, " cards received from Alice.")

    ## Deck encryption by Bob
    deck_bob = list()
    for i in range(5, num_cards):
        deck_bob.append(encryptCard(shuffled_deck_alice[i], bob_key))

    ## Send encrypted Bob cards to Alice
    print("Deck encrypted and shuffled.\n")
    print("Sending encrypted cards to Alice")
    shuffled_deck_bob = pickle.dumps(deck_bob, -1)
    client_alice.sendall(shuffled_deck_bob)


    ## Receive individually encrypted deck
    decrypted_bob_cards = client_alice.recv(4096)
    decrypted_bob_cards = pickle.loads(decrypted_bob_cards)
    print("Cards received from Alice.")

    for i in range(5):
        decrypted_bob_cards[i] = decryptCard(decrypted_bob_cards[i], bob_key)
    
    print("Cards decrypted.\n")

    print("Your cards are : ")
    print(decrypted_bob_cards)
    print("\n")
    
    ## Close connection
    client_alice.close()
   

if __name__ == '__main__':
    Main()

