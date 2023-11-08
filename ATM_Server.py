import socket
import threading
import datetime

# Configuración del servidor
host = '127.0.0.1'
port = 12345

# Nombre del archivo de registro
log_file = 'server_log.txt'

# Función para escribir un registro en el archivo de registro con fecha y hora
def log_event(event):
    with open(log_file, 'a') as log:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"{timestamp}: {event}\n")

# Cargando datos de usuarios desde un archivo de texto (simplificado)
users = {}
with open('users.txt', 'r') as file:
    for line in file:
        account_number, pin, balance = line.strip().split(',')
        users[account_number] = (pin, float(balance))

# Resto del código del servidor...

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
            elif data.startswith("transfer"):
                sender_account_number, receiver_account_number, amount = data.split()[1], data.split()[2], float(data.split()[3])
                success, new_balance = transfer(sender_account_number, receiver_account_number, amount)
                if success:
                    client_socket.send(f"Transferencia exitosa. Nuevo saldo: ${new_balance}".encode('utf-8'))
                else:
                    client_socket.send("Transferencia fallida. Fondos insuficientes o cuenta inexistente.".encode('utf-8'))
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
        balance = users[account_number][1]
        log_event(f"Consulta de saldo para la cuenta {account_number}. Saldo actual: ${balance}")
        return balance
    log_event(f"Intento de consulta de saldo para una cuenta inexistente: {account_number}")
    return 0

# Función para realizar un retiro
def withdraw(account_number, amount):
    if account_number in users:
        current_balance = users[account_number][1]
        if current_balance >= amount:
            new_balance = current_balance - amount
            users[account_number] = (users[account_number][0], new_balance)
            update_user_data()
            log_event(f"Retiro de ${amount} realizado en la cuenta {account_number}. Nuevo saldo: ${new_balance}")
            return True, new_balance
        log_event(f"Intento de retiro de ${amount} en la cuenta {account_number} sin fondos suficientes.")
    else:
        log_event(f"Intento de retiro en una cuenta inexistente: {account_number}")
    return False, 0

# Función para realizar un depósito
def deposit(account_number, amount):
    if account_number in users:
        current_balance = users[account_number][1]
        new_balance = current_balance + amount
        users[account_number] = (users[account_number][0], new_balance)
        update_user_data()
        log_event(f"Depósito de ${amount} realizado en la cuenta {account_number}. Nuevo saldo: ${new_balance}")
        return new_balance
    log_event(f"Intento de depósito en una cuenta inexistente: {account_number}")
    return 0

# Función para manejar las transferencias entre cuentas
def transfer(sender_account_number, receiver_account_number, amount):
    if sender_account_number in users and receiver_account_number in users:
        sender_balance = users[sender_account_number][1]
        if sender_balance >= amount:
            receiver_balance = users[receiver_account_number][1]
            sender_new_balance = sender_balance - amount
            receiver_new_balance = receiver_balance + amount
            users[sender_account_number] = (users[sender_account_number][0], sender_new_balance)
            users[receiver_account_number] = (users[receiver_account_number][0], receiver_new_balance)
            update_user_data()
            log_event(f"Transferencia de ${amount} de la cuenta {sender_account_number} a la cuenta {receiver_account_number}. Nuevo saldo del remitente: ${sender_new_balance}. Nuevo saldo del destinatario: ${receiver_new_balance}")
            return True, sender_new_balance
        else:
            log_event(f"Intento de transferencia de ${amount} de la cuenta {sender_account_number} a la cuenta {receiver_account_number} sin fondos suficientes.")
    else:
        log_event("Intento de transferencia entre cuentas inexistentes.")
    return False, 0


# Función para actualizar los datos de usuario en el archivo de texto
def update_user_data():
    with open('users.txt', 'w') as file:
        for account_number, (pin, balance) in users.items():
            file.write(f"{account_number},{pin},{balance}\n")

# Inicializar el socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)

log_event("Servidor ATM en ejecución...")

while True:
    client_socket, client_address = server_socket.accept()
    log_event(f"Conexión entrante de {client_address}")

    # Iniciar un hilo para manejar al cliente
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
