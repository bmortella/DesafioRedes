import argparse
import socket
import threading
from OpenSSL import SSL

parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str, default="127.0.0.1")
parser.add_argument('--port', type=int, default=41706)
parser.add_argument('--nossl', action="store_false")
parser.add_argument('--max_clients', type=int, default=5)
args = parser.parse_args()

IP = args.ip
PORT = args.port
BUFFER_SIZE = 2048
USE_SSL = args.nossl
MAX_CLIENTS = args.max_clients

# Criação de socket TCP do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if USE_SSL:
    # Configurando SSL
    context = SSL.Context(SSL.SSLv23_METHOD)
    context.use_certificate_file('cert.pem')
    context.use_privatekey_file('key.pem')
    server = SSL.Connection(context, server)

# Inicia o servidor
server.bind((IP, PORT))
server.listen(MAX_CLIENTS)
print(f"Servidor escutando na porta {PORT} com SSL {'ativo' if USE_SSL else 'inativo'}.")

client_list = list()

'''
Thread que lida com os clientes, a funcao dela eh receber
as mensagens, processar e enviar para os outros clientes
'''
class ClientThread(threading.Thread):
    
    def __init__(self, username, conn, addr):
        threading.Thread.__init__(self)
        self.username = username
        self.conn = conn
        self.addr = addr

    def disconnect(self):

        if USE_SSL:
            self.conn.shutdown()
        else:
            self.conn.close()

        client_list.remove(((self.conn, self.addr), self.username))
        print(f"Usuario {self.username} {addr} desconectado.") 
    
    def run(self):
        while True:
          
            msg = self.conn.recv(BUFFER_SIZE).decode("UTF-8")
            
            if msg == "quit":
                self.disconnect()
                break

            # Repassa a mensagem para os outros clientes
            for client in client_list:
                client_conn = client[0][0]
                if client_conn != self.conn:
                    client_conn.send(f"{self.username} : {msg}".encode("UTF-8"))
            


# Espera por conexoes e aceita
while True:

    conn, addr = server.accept()

    # Recebe nome de ate 12 caracteres
    username = conn.recv(12).decode("UTF-8")
    # Registra cliente
    client_list.append(((conn, addr), username))
    print(f"Usuario {username} {addr} conectado.")

    # Inicia thread
    ClientThread(username, conn, addr).start()