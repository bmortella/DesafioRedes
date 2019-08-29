import socket, threading #importa modulo socket

TCP_IP = '127.0.0.1' # endereço IP do servidor 
TCP_PORTA = 24000      # porta disponibilizada pelo servidor
TAMANHO_BUFFER = 1024

NOME  = input("Digite seu nome: ")

# Criação de socket TCP do cliente
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Conecta ao servidor em IP e porta especifica 
cliente.connect((TCP_IP, TCP_PORTA))
print("Conectado! Digite quit para sair.")

class Receiver(threading.Thread):

    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        while True:
            data, addr = self.conn.recvfrom(1024)
            print(data.decode("UTF-8"))

Receiver(cliente).start()

while True:
    msg = input(":> ")
    cliente.send("{}: {}".format(NOME, msg).encode("UTF-8"))
    if msg == "quit":
        break

cliente.close()
print("Desconectado.")


