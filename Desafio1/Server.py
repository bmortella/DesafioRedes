import socket #importa modulo socket
from OpenSSL import SSL
 
TCP_IP = '127.0.0.1' # endereço IP do servidor 
TCP_PORTA = 24000       # porta disponibilizada pelo servidor
TAMANHO_BUFFER = 1024     # definição do tamanho do buffer
 
# Criação de socket TCP
# SOCK_STREAM, indica que será TCP.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Configurando SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_certificate_file('cert.pem')
context.use_privatekey_file('key.pem')

# Embrulha o socket com o SSL
servidor = SSL.Connection(context, sock)

servidor.bind((TCP_IP, TCP_PORTA))

#Define o limite de conexões. 
servidor.listen(1)

print("Servidor dispoivel na porta 5005 e escutando.....") 

# Aceita conexão
conn, addr = servidor.accept()
print ('Endereço conectado:', addr)
while 1:
    #dados retidados da mensagem recebida
    
    try:
        data = conn.recv(TAMANHO_BUFFER)

        if data: 
            print ("Mensagem recebida:", data.decode("UTF-8"))  
            conn.send(data.upper())  # envia dados recebidos em letra maiuscula

    except SSL.ZeroReturnError: #Quando a conexao eh fechada pelo cliente
        conn.shutdown()
        sock.close()
        break

