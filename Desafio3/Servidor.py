import socket, threading

TCP_IP = '127.0.0.1' # endereço IP do servidor 
TCP_PORTA = 24000      # porta disponibilizada pelo servidor
TAMANHO_BUFFER = 1024     # definição do tamanho do buffer

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# IP e porta que o servidor deve aguardar a conexão
servidor.bind((TCP_IP, TCP_PORTA))

servidor.listen(5)

conexoes = list()

class Handler(threading.Thread):

    def __init__(self, name, conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        connected = True
        while connected:
            data = self.conn.recv(TAMANHO_BUFFER)

            if data == "quit":
                print("Cliente {} desconectado.".format(self.conn))
                break

            #Passa mensagem para os outros clientes
            for conexao in conexoes:
                if conexao != self.conn:
                    conexao.send(data)

id = 0
while True:
    conn, addr = servidor.accept()
    print ('Endereço conectado:', addr)
    conexoes.append(conn)
    Handler(id, conn).start()

    id += 1




