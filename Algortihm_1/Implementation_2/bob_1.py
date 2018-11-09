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

    shuffled_deck_alice = client_alice.recv(4096)
    shuffled_deck_alice = pickle.loads(shuffled_deck_alice)

    num_cards = len(shuffled_deck_alice)
    bob_key = 2
    print("A deck of ",num_cards," cards received from Alice.")

    ## Deck encryption by bob
    deck_bob = list()
    for i in range(num_cards):
        deck_bob.append(encryptCard(shuffled_deck_alice[i], bob_key))

    ## Shuffle
    random.shuffle(deck_bob)

    ## This is used in final verification phase
    final_deck_before_individual_keys = list()
    for i in range(num_cards):
        final_deck_before_individual_keys.append(decryptCard(deck_bob[i], bob_key))

    ## Send encrypted deck to Alice
    print("Deck encrypted and shuffled.\n")
    shuffled_deck_bob = pickle.dumps(deck_bob, -1)
    client_alice.sendall(shuffled_deck_bob)
    print("Deck sent back to Alice.\n")

    ## Receive individually encrypted deck
    shuffled_deck_bob = client_alice.recv(4096)
    shuffled_deck_bob = pickle.loads(shuffled_deck_bob)
    print("Deck received from Alice.")

    for i in range(num_cards):
        shuffled_deck_bob[i] = decryptCard(shuffled_deck_bob[i], bob_key)
    
    print("Deck decrypted.\n")

    print("Getting individual keys...")
    bob_individual_keys = random.sample(range(1, 60), num_cards)
    for i in range(num_cards):
        shuffled_deck_bob[i] = encryptCard(shuffled_deck_bob[i], bob_individual_keys[i])
    print("Deck encrypted by individual keys.\n")

    shuffled_encrypted_cards = pickle.dumps(shuffled_deck_bob, -1)
    client_alice.sendall(shuffled_encrypted_cards)
    print("Deck sent to Alice.\n")

    print("Distributing cards...\n")

    ## Receive Alice's keys for Bob's cards
    bob_cards_keys2 = client_alice.recv(4096)
    bob_cards_keys2 = pickle.loads(bob_cards_keys2)

    bob_cards = []
    bob_cards_keys1 = []
    alice_cards_keys2 = []

    for i in range(1,num_cards,2):
        bob_cards.append(shuffled_deck_bob[i])
        bob_cards_keys1.append(bob_individual_keys[i])
    
    for i in range(0,num_cards,2):
        alice_cards_keys2.append(bob_individual_keys[i])

    print("A hand of ",num_cards//2," cards received.\n")
    print("Individual keys received.\n")
    print("Sending individual keys of Alice's cards...\n")

    alice_cards_keys2 = pickle.dumps(alice_cards_keys2, -1)
    client_alice.sendall(alice_cards_keys2)
    print('Sent.\n')

    print("Decrypting your cards...\n")
    bob_cards_decrypted = [0 for i in range(num_cards//2)]
    for i in range(num_cards//2):
        bob_cards_decrypted[i] = decryptCard(decryptCard(bob_cards[i], bob_cards_keys1[i]), bob_cards_keys2[i])

    print("Your cards are : ")
    print(bob_cards_decrypted)
    print("\n")

    print("We can start the game now..")

    sum_cards_bob = sum(bob_cards_decrypted)
    print("Sum of your cards: ", sum_cards_bob)
    
    ## Send your sum to Alice
    sendKey(client_alice, str(sum_cards_bob))

    ## Receive Alice's sum of cards
    sum_cards_alice = int(client_alice.recv(1024).decode('ascii'))
    print("Sum of Alice's cards: ", sum_cards_alice)

    if(sum_cards_alice < sum_cards_bob):
        print("Congrats! You won!")
    elif(sum_cards_alice == sum_cards_bob):
        print("It's a Draw!")
    else:
        print("Alas! Alice wins!")

    print("\n\nVerification Phase...")
    
    print("Receiving original key from Alice...")
    alice_key = int(client_alice.recv(1024).decode('ascii'))

    print("Sending original key to Alice...")

    ## Send you own key to Bob for verification
    sendKey(client_alice, str(bob_key))

    sum_cards_alice_verified = 0
    for i in range(0, num_cards, 2):
        sum_cards_alice_verified = sum_cards_alice_verified + decryptCard(final_deck_before_individual_keys[i], alice_key)
    
    print("Alice's card value: ", sum_cards_alice_verified)
    
    client_alice.close()
   

if __name__ == '__main__':
    Main()

