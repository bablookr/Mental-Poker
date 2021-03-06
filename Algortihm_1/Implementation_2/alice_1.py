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
    num_cards = random.randrange(10, 53, 2)
    alice_key = 1

    ## Deck has even number of cards from 10 to 52
    deck = random.sample(range(1, 53), num_cards)
    print("A deck of ", num_cards, " cards received.")

    ## Deck encryption by Alice
    for i in range(num_cards):
        deck[i] = encryptCard(deck[i], alice_key)
    
    ## Shuffle deck    
    random.shuffle(deck)
    print("Deck encrypted and shuffled.\n")

    ## Send deck to Bob
    sendDeck(connection_from_bob, address_bob, deck)
    print("Deck sent to Bob.\n")

    ## Receive encrypted and shuffled deck from Bob
    shuffled_deck_bob = connection_from_bob.recv(4096)
    shuffled_deck_bob = pickle.loads(shuffled_deck_bob)
    print("Deck received from Bob.")

    ## Decrypt deck before individual encryption
    for i in range(num_cards):
        shuffled_deck_bob[i] = decryptCard(shuffled_deck_bob[i], alice_key)

    print("Deck decrypted.\n")


    ## This is used in final verification phase
    final_deck_before_individual_keys = list()
    for i in range(num_cards):
        final_deck_before_individual_keys.append(shuffled_deck_bob[i])

    print("Getting individual keys...")
    alice_individual_keys = random.sample(range(1, 60), num_cards)
    ## Encrypt each card with its individual key
    for i in range(num_cards):
        shuffled_deck_bob[i] = encryptCard(shuffled_deck_bob[i], alice_individual_keys[i])
    print("Deck encrypted by individual keys.\n")

    ## Send deck to Bob for individual encryption
    sendDeck(connection_from_bob, address_bob, shuffled_deck_bob)
    print("Deck sent to Bob.\n")

    ## Receive final deck from Bob
    shuffled_encrypted_cards = connection_from_bob.recv(4096)
    shuffled_encrypted_cards = pickle.loads(shuffled_encrypted_cards)
    print("Deck received from Bob.")

    ## Distribute cards in half
    print("Distributing cards...\n")

    alice_cards = []
    alice_cards_keys1 = []
    bob_cards_keys2 = []

    ## Alice gets even indexed cards
    for i in range(0, num_cards, 2):
        alice_cards.append(shuffled_encrypted_cards[i])
        alice_cards_keys1.append(alice_individual_keys[i])
    
    ## Bob gets odd indexed cards
    for i in range(1, num_cards, 2):
        bob_cards_keys2.append(alice_individual_keys[i])

    print("A hand of ",num_cards//2," cards received.\n")
    
    ## We need individual keys of both players for total decryption
    print("Sending individual keys of Bob's cards...\n")
    sendDeck(connection_from_bob, address_bob, bob_cards_keys2)
    print("Sent.")

    print("Requesting individual keys from Bob...")
    alice_cards_keys2 = connection_from_bob.recv(4096)
    alice_cards_keys2 = pickle.loads(alice_cards_keys2)
    print("Individual keys Received.\n")

    ## Decrypt to see the hand you are dealt
    print("Decrypting your cards...\n")
    alice_cards_decrypted = [ 0 for i in range(num_cards // 2) ]
    for i in range(num_cards//2):
        alice_cards_decrypted[i] = decryptCard(decryptCard(alice_cards[i], alice_cards_keys1[i]), alice_cards_keys2[i])

    print("Your cards are : ")
    print(alice_cards_decrypted)
    print("\n")

    print("We can start the game now..")

    sum_cards_alice = sum(alice_cards_decrypted)
    print("Sum of your cards: ", sum_cards_alice)
    
    ## Receive Bob's sum of cards
    sum_cards_bob = int(connection_from_bob.recv(1024).decode('ascii'))
    print("Sum of Bob's cards: ", sum_cards_bob)

    ## Send your sum to Bob
    sendKey(connection_from_bob, str(sum_cards_alice))

    if(sum_cards_alice > sum_cards_bob):
        print("Congrats! You won!")
    elif(sum_cards_alice == sum_cards_bob):
        print("It's a Draw!")
    else:
        print("Alas! Bob wins!")

    print("\n\nVerification Phase...")

    print("Sending original key to Bob...")
    ## Send you own key to Bob for verification
    sendKey(connection_from_bob, str(alice_key))
    
    print("Receiving original key from Bob...")
    bob_key = int(connection_from_bob.recv(4096).decode('ascii'))

    sum_cards_bob_verified = 0
    for i in range(1, num_cards, 2):
        sum_cards_bob_verified = sum_cards_bob_verified + decryptCard(final_deck_before_individual_keys[i], bob_key)
    
    print("Bob's card value: ", sum_cards_bob_verified)
    connection_from_bob.close()
    server_alice.close()


if __name__ == '__main__':
    Main()
