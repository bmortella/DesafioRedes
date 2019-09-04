import os
import argparse
import socket
import threading
from pathlib import Path
from OpenSSL import SSL

parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str, default="127.0.0.1")
parser.add_argument('--port', type=int, default=41706)
parser.add_argument('--nossl', action="store_false")
parser.add_argument('--max_clients', type=int, default=5)
parser.add_argument('--username', type=str, default=None)
args = parser.parse_args()

# Configuracoes basicas
IP = args.ip
PORT = args.port
BUFFER_SIZE = 2048
USE_SSL = args.nossl
COMMAND_PREFIX = '/'
FILES_DIR = 'downloads/'

# Criação de socket TCP do cliente
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if USE_SSL:
    # Configurando SSL
    context = SSL.Context(SSL.SSLv23_METHOD)
    context.use_certificate_file('cert.pem')
    context.use_privatekey_file('key.pem')
    client = SSL.Connection(context, client)

username = args.username
if not username:
    username = input("Digite seu nome: ")
# Garantimos que o nome tenha 12 caracteres
if len(username) > 12:
    username = username[:12]

# Conecta ao servidor
client.connect((IP, PORT))

# Envia nome de usuario
client.send(username.encode("UTF-8"))
print(f"Conectado como {username}! Digite /quit para sair.")

# Thread para receber mensagens do servidor
class Receiver(threading.Thread):

    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        while True:
            try:
                msg = self.conn.recv(BUFFER_SIZE).decode("UTF-8")

                # Quando o servidor for enviar um arquivo requisitado
                if msg.startswith(COMMAND_PREFIX + "download"):
                    download_args = msg.split()
                    file_path = Path(FILES_DIR) / Path(download_args[1])
                    file_size = int(download_args[2])

                    print(f"[!] Recebendo {file_path.name}.")
                    received = 0
                    with open(file_path, 'wb') as f:
                        while received < file_size:
                            data = self.conn.recv(BUFFER_SIZE)
                            f.write(data)
                            received += len(data)
                    print(f"[!] Arquivo recebido.")

                else:
                    print(msg)
            #Acontece quando o servidor ou o cliente termina a conexao
            except SSL.ZeroReturnError:
                print("[!] Desconectado!")
                break
            # O mesmo porem quando o SSL esta desativado
            except ConnectionAbortedError:
                print("[!] Desconectado!")
                break

# Iniciamos a thread apos conectarmos com o servidor
receiver_thread = Receiver(client)
receiver_thread.start()

# Loop para enviar mensagens ao servidor
while True:
    msg = input()

    if msg.startswith(COMMAND_PREFIX):
        
        # Separa argumentos
        cmd_args = msg.split()
        # Remove prefixo do comando e coloca tudo em letra minuscula
        cmd_args[0] = cmd_args[0][1:].lower()

        if cmd_args[0] == "quit":
            # Enviamos o comando para que o servidor tambem feche a conexao
            client.send(msg.encode("UTF-8"))
            if USE_SSL:
                client.shutdown()
            else:
                client.close()
            break

        elif cmd_args[0] == "upload":

            file_path = Path(cmd_args[1])
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
            client.send(msg.encode("UTF-8"))
            #print("[!] Esse comando não existe.")
    else:
        client.send(msg.encode("UTF-8"))
            