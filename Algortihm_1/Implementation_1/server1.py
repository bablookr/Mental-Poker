import socket
import pickle
import _thread
import time
import random
from phe import paillier



def clientthread(conn,addr,public_key,rand_no):
    print("SERVER 1:Connection from: " + str(addr))
    dicti = {"rand_no":rand_no, "public_key":public_key}
    data = pickle.dumps(dicti, -1)
    conn.sendall(data)


def sendresult(conn,result):
    conn.send(result.encode('ascii'))
    

def Main():
    public_key, private_key = paillier.generate_paillier_keypair()
    rand_no = random.randint(5,10)
    host1 = "127.0.0.1"
    port1 = 5004

    server_sock1 = socket.socket()
    server_sock1.bind((host1, port1))
    server_sock1.listen(3)

    print("SERVER 1: Waiting for connection...")
   
  
    conn1, addr1 = server_sock1.accept() # connection from client1
    clientthread(conn1, addr1, public_key, rand_no)

    conn2, addr2 = server_sock1.accept() # connection from client2
    clientthread(conn2, addr2, public_key, rand_no)

    conn3, addr3 = server_sock1.accept() # connection from server2

    alice_score = 0
    bob_score = 0

    for i in range(5):
        enc_diff_sal_stream = conn3.recv(4096)
        enc_diff_sal = pickle.loads(enc_diff_sal_stream)
        diff  = private_key.decrypt(enc_diff_sal)
        if (diff > 0):
            result = 'Alice wins'+ "\r\n"
            alice_score+=1
        else:
            result = 'Bob wins'+ "\r\n"
            bob_score+=1

        sendresult(conn1,result)
        sendresult(conn2,result)

    if(alice_score > bob_score):
        final_result = 'WINNER: Alice' + "\r\n"
    elif(alice_score == bob_score):
        final_result = 'A draw!' +  "\r\n"
    else:
        final_result = 'WINNER: Bob' + "\r\n"

    sendresult(conn1,final_result)
    sendresult(conn2,final_result)

    ## Close all connections
    conn1.close()
    conn2.close()
    conn3.close()
    server_sock1.close()


if __name__ == '__main__':
    Main()
