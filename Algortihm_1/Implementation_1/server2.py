import socket
import pickle
import _thread
import time
from phe import paillier


def client(conn,addr):
    print("SERVER 2:Connection from: " + str(addr))
    encrypted_sal_stream = conn.recv(4096)
    encrypted_sal = pickle.loads(encrypted_sal_stream)
    return encrypted_sal


def Main():
    host1 = '127.0.0.1'
    port1 = 5004
      
    host2 = "127.0.0.1"
    port2 = 5005

    server_sock2 = socket.socket()
    server_sock21 = socket.socket()
    server_sock2.bind((host2, port2))
    server_sock2.listen(2)

    print("SERVER 2: Waiting for connection...")

    conn1, addr1 = server_sock2.accept()
    conn2, addr2 = server_sock2.accept()

    server_sock21.connect((host1, port1))
    
    for i in range(5):
        encrypted_salA = client(conn1,addr1)
        encrypted_salB = client(conn2,addr2)

        data = pickle.dumps(encrypted_salA-encrypted_salB,-1)
        server_sock21.sendall(data)
    
    ## Close all connections
    conn1.close()
    conn2.close()
    server_sock2.close()
    server_sock21.close()
    
if __name__ == '__main__':
    Main()
