## Without third party

import socket
import pickle
import _thread
import time
import random
from helpers import *

## Alice

def Main():
    ## Alice's server for initial reshuffling
    ## Set up server to connect to Bob
    server_alice = setServer('127.0.0.1', 5006, 2)

    print("Alice is up for the game.")
    print("Waiting for Bob to connect...\n")

    ## Connect with Bob to start shuffling the deck
    connection_from_bob, address_bob = server_alice.accept()
    print("Connected to Bob.\n")

    ## Set up initial game parameters
    num_cards = 10
    alice_key = 1

    ## Deck has even number of cards from 10 to 52
    deck = random.sample(range(1, 53), num_cards)
    print("A deck of ", num_cards, " cards generated")

    deck_orig = list()
    for i in range(10):
        deck_orig.append(deck[i])

    ## Deck encryption by Alice
    for i in range(num_cards):
        deck[i] = encryptCard(deck[i], alice_key)
    
    ## Shuffle deck    
    random.shuffle(deck)
    print("Deck encrypted and shuffled.\n")

    ## Send deck to Bob
    sendDeck(connection_from_bob, address_bob, deck)
    print("Deck sent to Bob.\n")

    ## Receive Alice's cards from Bob
    alice_cards = connection_from_bob.recv(4096)
    alice_cards = pickle.loads(alice_cards)
    print("Alice's cards received from Bob.")

    ## Receive Bob's cards from Bob
    bob_cards = connection_from_bob.recv(4096)
    bob_cards = pickle.loads(bob_cards)
    print("Bob's cards received from Bob.")
    
    ## Decrypt deck to get Alice's Cards and Bob's cards
    decrypted_alice_cards = list()
    decrypted_bob_cards = list()
    for i in range(5):
        decrypted_alice_cards.append(decryptCard(alice_cards[i], alice_key))
        decrypted_bob_cards.append(decryptCard(bob_cards[i], alice_key))
    
    print("Cards decrypted.\n")


    ## Send Bob's cards to Bob
    sendDeck(connection_from_bob, address_bob, decrypted_bob_cards)
    print("Sent Bob's cards...")

    print("Your cards are : ")
    print(decrypted_alice_cards)

    print("\n")

    time.sleep(0.1)
    connection_from_bob.close()
    server_alice.close()

    print()
    print("Initial Deck was:")
    print(deck_orig)
if __name__ == '__main__':
    Main()
