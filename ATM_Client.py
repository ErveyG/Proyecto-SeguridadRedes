import socket
import hashlib

# Configuración del cliente
host = '127.0.0.1'
port = 12345

# Clave compartida para cifrado (debe coincidir con la del servidor)
shared_key = 'my_shared_key'

# Función para cifrar datos
def encrypt(data):
    cipher = hashlib.sha256(shared_key.encode()).digest()
    encrypted_data = ''.join([chr((ord(data[i]) + ord(cipher[i % len(cipher)])) % 256) for i in range(len(data))])
    return encrypted_data


# Función para descifrar datos
def decrypt(data):
    cipher = hashlib.sha256(shared_key.encode()).digest()
    decrypted_data = ''.join([chr(ord(data[i]) - ord(cipher[i % len(cipher)])) for i in range(len(data))])
    return decrypted_data

# Función para interactuar con el cliente
def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    login_attempts = 0
    logged_in = False
    account_number = None

    try:
        while login_attempts < 3:
            if not logged_in:
                print("Opciones:")
                print("1. Iniciar sesión")
                print("2. Crear una nueva cuenta")
                choice = input("Seleccione una opción: ")

                if choice == "1":
                    account_number = input("Ingrese el número de cuenta: ")
                    pin = input("Ingrese su PIN: ")
                    client_socket.send(encrypt(f"login {account_number} {pin}"))
                    response = decrypt(client_socket.recv(1024).decode('utf-8'))
                    print(response)
                    print("------------------\n")
                    if response == "Login exitoso.":
                        logged_in = True
                        login_attempts = 0
                    else:
                        login_attempts += 1
                # ... (código para crear nueva cuenta)
                else:
                    print("Opción no válida")

        if login_attempts >= 3:
            print("Demasiados intentos de inicio de sesión. Saliendo.")
            return

        while True:
            if not logged_in:
                print("Sesión cerrada.")
                break

            print("Opciones:")
            print("1. Consultar saldo")
            print("2. Retirar dinero")
            print("3. Depositar dinero")
            print("4. Transferir dinero")
            print("5. Salir")

            choice = input("Seleccione una opción: ")

            if choice == "1":
                client_socket.send(encrypt(f"balance {account_number}"))
                response = decrypt(client_socket.recv(1024).decode('utf-8'))
                print(response)
                print("------------------\n")
            elif choice == "2":
                amount = float(input("Ingrese la cantidad a retirar: "))
                client_socket.send(encrypt(f"withdraw {account_number} {amount}"))
                response = decrypt(client_socket.recv(1024).decode('utf-8'))
                print(response)
                print("------------------\n")
            elif choice == "3":
                amount = float(input("Ingrese la cantidad a depositar: "))
                client_socket.send(encrypt(f"deposit {account_number} {amount}"))
                response = decrypt(client_socket.recv(1024).decode('utf-8'))
                print(response)
                print("------------------\n")
            elif choice == "4":
                receiver_account = input("Ingrese el número de cuenta de destino: ")
                amount = float(input("Ingrese la cantidad a transferir: "))
                client_socket.send(encrypt(f"transfer {account_number} {receiver_account} {amount}"))
                response = decrypt(client_socket.recv(1024).decode('utf-8'))
                print(response)
                print("------------------\n")
            elif choice == "5":
                client_socket.send(encrypt("exit"))
                break
            else:
                print("Opción no válida")

    finally:
        client_socket.close()

if __name__ == '__main__':
    main()
