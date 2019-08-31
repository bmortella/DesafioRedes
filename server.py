import argparse
import socket
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

while True:

    conn, addr = server.accept()

    username = conn.recv(12).decode("UTF-8")
    print(f"Usuario {username} {addr} conectado.")

    # Inicia thread
    break