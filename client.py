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
COMMAND_PREFIX = '/'

# Criação de socket TCP do cliente
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if USE_SSL:
    # Configurando SSL
    context = SSL.Context(SSL.SSLv23_METHOD)
    context.use_certificate_file('cert.pem')
    context.use_privatekey_file('key.pem')
    client = SSL.Connection(context, client)

username = input("Digite seu nome: ")
# Garantimos que o nome tenha 12 caracteres
if len(username) > 12:
    username = username[:12]

# Conecta ao servidor
client.connect((IP, PORT))

# Envia nome de usuario
client.send(username.encode("UTF-8"))
print(f"Conectado como {username}!")

class Receiver(threading.Thread):

    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        while True:
            try:
                msg = self.conn.recv(BUFFER_SIZE).decode("UTF-8")
                print(msg)
            #Acontece quando o servidor ou o cliente termina a conexao
            except SSL.ZeroReturnError:
                print("Desconectado!")
                break
            # O mesmo porem quando o SSL esta desativado
            except ConnectionAbortedError:
                print("Desconectado!")
                break

receiver_thread = Receiver(client)
receiver_thread.start()

while True:
    msg = input()
    client.send(msg.encode("UTF-8"))

    if msg.startswith(COMMAND_PREFIX):
        # Remove prefixo da mensagem
        msg = msg[1:]
        
        # Separa argumentos
        cmd_args = msg.split()

        if cmd_args[0].lower() == "quit":
            if USE_SSL:
                client.shutdown()
            else:
                client.close()
            break