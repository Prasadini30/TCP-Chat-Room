import threading
import socket
import os

alias = input('Choose an alias >>> ')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect(('127.0.0.1', 59000))
except Exception as e:
    print(f"Connection failed: {e}")
    exit()

# Function to save chat history
def save_message(message):
    with open("chat_history.txt", "a", encoding="utf-8") as file:
        file.write(message + "\n")

# Receiving messages from the server
def client_receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == "alias?":
                client.send(alias.encode('utf-8'))
            else:
                print(message)
                save_message(message)  # Save to history
        except:
            print('Error! Connection lost.')
            client.close()
            break

# Sending messages to the server
def client_send():
    while True:
        try:
            message = input("")
            
            # Exit command
            if message.lower() == "/exit":
                client.send(f"{alias} has left the chat.".encode('utf-8'))
                client.close()
                print("Disconnected from chat.")
                os._exit(0)

            # Request online users
            elif message.lower() == "/users":
                client.send("/users".encode('utf-8'))

            # Private messaging format: @username message
            elif message.startswith("@"):
                client.send(message.encode('utf-8'))
            else:
                client.send(f'{alias}: {message}'.encode('utf-8'))

        except:
            print('Error! Unable to send message.')
            client.close()
            break

# Start receiving thread
receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

# Start sending thread
send_thread = threading.Thread(target=client_send)
send_thread.start()
