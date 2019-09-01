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
args = parser.parse_args()

IP = args.ip
PORT = args.port
BUFFER_SIZE = 2048
USE_SSL = args.nossl
MAX_CLIENTS = args.max_clients
COMMAND_PREFIX = '/'
FILES_DIR = 'envios'

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


def server_broadcast(msg):
    for client in client_list:
        client[0][0].send(msg.encode("UTF-8"))


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

        try:
            if USE_SSL:
                self.conn.shutdown()
            else:
                self.conn.close()
        except:
            pass
        finally:
            client_list.remove(((self.conn, self.addr), self.username))
            print(f"Usuario {self.username} {self.addr} desconectado.")
            server_broadcast(f"Usuario {self.username} se desconectou.")
    
    def run(self):
        while True:
          
            msg = self.conn.recv(BUFFER_SIZE).decode("UTF-8")
            
            # Verifica se mensagem eh um comando
            if msg.startswith(COMMAND_PREFIX):
                # Remove prefixo da mensagem
                msg = msg[1:]
                
                # Separa argumentos
                cmd_args = msg.split()
                cmd_args[0] = cmd_args[0].lower()

                if cmd_args[0] == "quit":
                    self.disconnect()
                    break
                elif cmd_args[0] == "users":
                    reply = "[!] Usuarios conectados:"
                    for client in client_list:
                        reply += f"\n{client[1]}"
                    self.conn.send(reply.encode("UTF-8"))
                elif cmd_args[0] == "ls":
                    reply = "[!] Arquivos:"
                    for item in Path(FILES_DIR).iterdir():
                        if item.is_file():
                            reply += f"\n{item.name}"
                    self.conn.send(reply.encode("UTF-8"))
                elif cmd_args[0] == "upload":
                    file_name = cmd_args[1]
                    file_size = int(cmd_args[2])

                    received = 0
                    with open("envios/" + file_name, "wb") as f:
                        print(f"Recebendo arquivo {file_name} ({file_size} bytes) do usuario {self.username}")
                        while received < file_size:
                            data = self.conn.recv(BUFFER_SIZE)
                            f.write(data)
                            received += len(data)
                        print(f"Arquivo {file_name} ({file_size} bytes) do usuario {self.username} recebido.")
                else:
                    self.conn.send("[!] Esse comando não existe.")

                    
            else:
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
    server_broadcast(f"Usuario {username} se conectou.")

    # Inicia thread
    ClientThread(username, conn, addr).start()