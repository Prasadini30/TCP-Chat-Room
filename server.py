import threading
import socket

host = '127.0.0.1'
port = 59000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
aliases = {}

def broadcast(message, sender=None):
    """Send a message to all connected clients except the sender."""
    for client in clients:
        if client != sender:
            client.send(message)

def private_message(sender_alias, target_alias, message):
    """Send a private message to a specific user."""
    if target_alias in aliases.values():
        target_client = list(aliases.keys())[list(aliases.values()).index(target_alias)]
        target_client.send(f"(Private) {sender_alias}: {message}".encode('utf-8'))
    else:
        sender_client = list(aliases.keys())[list(aliases.values()).index(sender_alias)]
        sender_client.send(f"User {target_alias} not found.".encode('utf-8'))

def handle_client(client):
    """Handles incoming messages from a specific client."""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')

            if not message:
                break  # Exit loop if the client sends an empty message (disconnect)

            sender_alias = aliases[client]

            # Handle private messages
            if message.startswith("@"):
                parts = message.split(" ", 1)
                if len(parts) > 1:
                    target_alias, msg_content = parts
                    target_alias = target_alias[1:]  # Remove '@' symbol
                    private_message(sender_alias, target_alias, msg_content)
                else:
                    client.send("Invalid private message format. Use @username message".encode('utf-8'))
            
            # Handle user list request
            elif message == "/users":
                user_list = ", ".join(aliases.values())
                client.send(f"Online users: {user_list}".encode('utf-8'))
            
            # Handle exit command
            elif message == "/exit":
                remove_client(client)
                break

            else:
                broadcast(f"{sender_alias}: {message}".encode('utf-8'), sender=client)

        except:
            remove_client(client)
            break

def remove_client(client):
    """Remove a client from the server and notify others."""
    if client in clients:
        alias = aliases[client]
        clients.remove(client)
        del aliases[client]
        client.close()
        broadcast(f"{alias} has left the chat room!".encode('utf-8'))
        print(f"{alias} has disconnected.")

def receive():
    """Accepts new client connections."""
    while True:
        print('Server is running and listening...')
        client, address = server.accept()
        print(f'Connection established with {str(address)}')

        client.send('alias?'.encode('utf-8'))
        alias = client.recv(1024).decode('utf-8')

        aliases[client] = alias
        clients.append(client)

        print(f'The alias of this client is {alias}')
        broadcast(f'{alias} has connected to the chat room!'.encode('utf-8'))
        client.send('You are now connected!'.encode('utf-8'))

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    receive()
