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