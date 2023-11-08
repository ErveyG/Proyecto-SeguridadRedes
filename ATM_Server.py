import socket
import threading

# Configuración del servidor
host = '127.0.0.1'
port = 12345

# Cargando datos de usuarios desde un archivo de texto (simplificado)
users = {}
with open('users.txt', 'r') as file:
    for line in file:
        account_number, pin, balance = line.strip().split(',')
        users[account_number] = (pin, float(balance))

# Función para manejar la conexión con un cliente
def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break

            if data == "exit":
                break
            elif data.startswith("login"):
                account_number, pin = data.split()[1], data.split()[2]
                if authenticate_user(account_number, pin):
                    client_socket.send("Login exitoso.".encode('utf-8'))
                else:
                    client_socket.send("PIN incorrecto o cuenta inexistente.".encode('utf-8'))
            elif data.startswith("balance"):
                account_number = data.split()[1]
                balance = get_balance(account_number)
                client_socket.send(f"Saldo actual: ${balance}".encode('utf-8'))
            elif data.startswith("withdraw"):
                account_number, amount = data.split()[1], float(data.split()[2])
                success, new_balance = withdraw(account_number, amount)
                if success:
                    client_socket.send(f"Retiro exitoso. Nuevo saldo: ${new_balance}".encode('utf-8'))
                else:
                    client_socket.send("Fondos insuficientes.".encode('utf-8'))
            elif data.startswith("deposit"):
                account_number, amount = data.split()[1], float(data.split()[2])
                new_balance = deposit(account_number, amount)
                client_socket.send(f"Depósito exitoso. Nuevo saldo: ${new_balance}".encode('utf-8'))
            else:
                client_socket.send("Comando no válido.".encode('utf-8'))

    finally:
        client_socket.close()

# Función para autenticar al usuario
def authenticate_user(account_number, pin):
    if account_number in users and users[account_number][0] == pin:
        return True
    return False

# Función para obtener el saldo de un usuario
def get_balance(account_number):
    if account_number in users:
        return users[account_number][1]
    return 0

# Función para realizar un retiro
def withdraw(account_number, amount):
    if account_number in users:
        current_balance = users[account_number][1]
        if current_balance >= amount:
            new_balance = current_balance - amount
            users[account_number] = (users[account_number][0], new_balance)
            update_user_data()
            return True, new_balance
    return False, 0

# Función para realizar un depósito
def deposit(account_number, amount):
    if account_number in users:
        current_balance = users[account_number][1]
        new_balance = current_balance + amount
        users[account_number] = (users[account_number][0], new_balance)
        update_user_data()
        return new_balance

# Función para actualizar los datos de usuario en el archivo de texto
def update_user_data():
    with open('users.txt', 'w') as file:
        for account_number, (pin, balance) in users.items():
            file.write(f"{account_number},{pin},{balance}\n")

# Inicializar el socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)

print("Servidor ATM en ejecución...")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Conexión entrante de {client_address}")

    # Iniciar un hilo para manejar al cliente
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
