import socket #importa modulo socket

TCP_IP = '127.0.0.1' # endereço IP do servidor 
TCP_PORTA = 24000      # porta disponibilizada pelo servidor
TAMANHO_BUFFER = 2048

MENSAGEM  = input("Digite sua mensagem para o servidor: ")

# Criação de socket TCP do cliente
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Conecta ao servidor em IP e porta especifica 
cliente.connect((TCP_IP, TCP_PORTA))

# envia mensagem para servidor 
cliente.send(MENSAGEM.encode('UTF-8'))

# recebe dados do servidor 
data, addr = cliente.recvfrom(TAMANHO_BUFFER)

# fecha conexão com servidor
cliente.close()

print ("received data:", data)
