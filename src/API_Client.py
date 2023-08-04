# import socket

# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # server_ip = input("Enter the server ip address: ")
# client.connect(("ef9e-67-242-95-192.ngrok-free.app", 5000))

# print(client.recv(1024).decode())
# client.send("Hello, I am a client".encode())
# # while True:
# #     question = input("Enter your question: ")
# #     if question == "quit":
# #         break
# #     else:
# #         print(llm_chain.run(question))


# #     question = input("Enter your question: ")
# #     client.send(question.encode())
# #     if question == "quit":
# #         break
# #     else:
# #         print(client.recv(1024).decode())

# import socket

# def start_client():
#     host = '733b-67-242-95-192.ngrok-free.app'
#     port = 5000
#     client_socket = socket.socket()  
#     client_socket.connect((host, port)) 
#     message = input(" -> ") 
#     while message.lower().strip() != 'bye':
#         client_socket.send(message.encode()) 
#         data = client_socket.recv(1024).decode() 
#         print('Received from server: ' + data) 
#         message = input(" -> ")  
#     client_socket.close() 

# if __name__ == '__main__':
#     start_client()


import socket

def start_client():
    host = "820c-67-242-95-192.ngrok.io"  # The host provided by ngrok
    port = 7860  # The port provided by ngrok
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print(client.recv(1024).decode())
    client.send("Hello, I am a client".encode())
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # s.connect((host, port))

    # msg = 'Hello, Server!'
    # s.send(msg.encode('utf-8'))

    # print(s.recv(1024).decode('utf-8'))

    # s.close()

if __name__ == '__main__':
    start_client()
