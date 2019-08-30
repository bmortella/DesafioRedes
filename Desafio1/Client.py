import socket #importa modulo socket
from OpenSSL import SSL

TCP_IP = '127.0.0.1' # endereço IP do servidor 
TCP_PORTA = 24000      # porta disponibilizada pelo servidor
TAMANHO_BUFFER = 1024

# Criação de socket TCP do cliente
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Configurando SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_certificate_file('cert.pem')
context.use_privatekey_file('key.pem')

# Embrulha o socket com o SSL
cliente = SSL.Connection(context, sock)

# Conecta ao servidor em IP e porta especifica
cliente.connect((TCP_IP, TCP_PORTA))

MENSAGEM = ""
while MENSAGEM.lower() != "quit":
    MENSAGEM  = input("Digite sua mensagem para o servidor: ")
    
    # envia mensagem para servidor 
    cliente.send(MENSAGEM.encode('UTF-8'))

    # recebe dados do servidor 
    data = cliente.recv(TAMANHO_BUFFER)

# Fecha conexão com servidor
cliente.shutdown()
sock.close()

print ("received data:", data.decode("UTF-8"))
