import socket
import threading
import hashlib
import datetime

# Configuración del servidor
host = '0.0.0.0'
port = 12345

# Clave compartida para cifrado (en un entorno real, esto debe ser más seguro)
shared_key = 'my_shared_key'

# Archivo de registro
log_file = "server_log.txt"

# Datos de usuarios (cuenta: (pin, saldo))
users = {}
# Leer los datos de usuario desde el archivo users.txt
with open("users.txt", "r") as user_file:
    for line in user_file:
        account, pin, balance = line.strip().split()
        users[account] = (pin, float(balance))

# Función para cifrar datos
def encrypt(data):
    cipher = hashlib.sha256(shared_key.encode()).digest()
    encrypted_data = ''.join([chr((ord(data[i]) + ord(cipher[i % len(cipher)])) % 256) for i in range(len(data))])
    return encrypted_data

# Función para descifrar datos
def decrypt(data):
    cipher = hashlib.sha256(shared_key.encode()).digest()
    decrypted_data = ''.join([chr((ord(data[i]) - ord(cipher[i % len(cipher)])) % 256) for i in range(len(data))])
    return decrypted_data

# Función para escribir registros en el archivo de registro
def log_event(event):
    with open(log_file, "a") as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} - {event}\n")

# Función para autenticar al usuario leyendo datos desde el archivo users.txt
def authenticate_user(account_number, pin):
    if account_number in users and users[account_number][0] == pin:
        return True
    return False

# Función para procesar transferencias
def transfer_funds(sender_account, receiver_account, amount):
    if sender_account in users and receiver_account in users:
        sender_balance = users[sender_account][1]
        if sender_balance >= amount:
            # Realizar la transferencia
            users[sender_account] = (users[sender_account][0], sender_balance - amount)
            users[receiver_account] = (users[receiver_account][0], users[receiver_account][1] + amount)
            return True
    return False

# Función para manejar la conexión con un cliente
def handle_client(client_socket):
    try:
        login_attempts = 0
        logged_in = False
        account_number = None

        while login_attempts < 3:
            data = decrypt(client_socket.recv(1024).decode('utf-8'))
            if not data:
                break

            if data == "exit":
                break
            elif data.startswith("login"):
                # Autenticación del usuario
                account_number, pin = data.split()[1], data.split()[2]
                if authenticate_user(account_number, pin):
                    client_socket.send(encrypt("Login exitoso."))
                    login_attempts = 0
                    logged_in = True
                    log_event(f"Inicio de sesión exitoso para la cuenta {account_number}")
                else:
                    login_attempts += 1
                    client_socket.send(encrypt("PIN incorrecto o cuenta inexistente."))
                    log_event(f"Intento de inicio de sesión fallido para la cuenta {account_number}")
            elif logged_in:
                if data.startswith("transfer"):
                    # Realizar transferencia
                    sender_account, receiver_account, amount = data.split()[1], data.split()[2], float(data.split()[3])
                    if transfer_funds(sender_account, receiver_account, amount):
                        client_socket.send(encrypt(f"Transferencia exitosa. Nuevo saldo: {users[sender_account][1]}"))
                        log_event(f"Transferencia de {amount} desde {sender_account} a {receiver_account}")
                    else:
                        client_socket.send(encrypt("Error en la transferencia. Verifique los datos."))
                else:
                    client_socket.send(encrypt("Comando no válido."))

    finally:
        client_socket.close()

# Configurar el servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)
print(f"Servidor escuchando en {host}:{port}")

# Aceptar conexiones entrantes
while True:
    client_socket, client_address = server_socket.accept()
    print(f"Conexión entrante de {client_address}")

    # Iniciar un hilo para manejar al cliente
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
