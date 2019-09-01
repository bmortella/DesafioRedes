import os
import argparse
import socket
import threading
import pathlib
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
print(f"Conectado como {username}! Digite /quit para sair.")

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
                print("[!] Desconectado!")
                break
            # O mesmo porem quando o SSL esta desativado
            except ConnectionAbortedError:
                print("[!] Desconectado!")
                break

receiver_thread = Receiver(client)
receiver_thread.start()

while True:
    msg = input()

    if msg.startswith(COMMAND_PREFIX):
        
        # Separa argumentos
        cmd_args = msg.split()
        # Remove prefixo do comando e coloca tudo em letra minuscula
        cmd_args[0] = cmd_args[0][1:].lower()

        if cmd_args[0] == "quit":
            client.send(msg.encode("UTF-8"))
            if USE_SSL:
                client.shutdown()
            else:
                client.close()
            break
        elif cmd_args[0] == "upload":

            file_path = pathlib.Path(cmd_args[1])
            if file_path.exists() and not file_path.is_dir():
                file_name = file_path.name
                file_size = os.stat(file_path).st_size

                msg = f"{COMMAND_PREFIX}upload {file_name} {file_size}"
                client.send(msg.encode("UTF-8"))

                print("[!] Enviando arquivo")
                with open(file_path, "rb") as f:
                    data = f.read(BUFFER_SIZE)
                    while data:
                        client.send(data)
                        data = f.read(BUFFER_SIZE)
                print("[!] Arquivo enviado")
            else:
                print("[!] Arquivo nao encontrado.")
        else:
            print("[!] Esse comando não existe.")
    else:
        client.send(msg.encode("UTF-8"))
            