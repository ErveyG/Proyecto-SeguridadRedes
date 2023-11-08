import socket

# Configuración del cliente
host = '127.0.0.1'
port = 12345

# Función para interactuar con el cliente
def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    logged_in = False
    account_number = None

    try:
        while True:
            if not logged_in:
                account_number = input("Ingrese el número de cuenta: ")
                pin = input("Ingrese su PIN: ")
                client_socket.send(f"login {account_number} {pin}".encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                if response == "Login exitoso.":
                    logged_in = True
                else:
                    print(response)
                    print("----------\n")
            else:
                print("Opciones:")
                print("1. Consultar saldo")
                print("2. Retirar dinero")
                print("3. Depositar dinero")
                print("4. Transferir dinero")
                print("5. Salir")
                print("----------\n")

                choice = input("Seleccione una opción: ")

                if choice == "1":
                    client_socket.send(f"balance {account_number}".encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')
                    print(response)
                    print("----------\n")
                elif choice == "2":
                    amount = float(input("Ingrese la cantidad a retirar: "))
                    client_socket.send(f"withdraw {account_number} {amount}".encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')
                    print(response)
                    print("----------\n")
                elif choice == "3":
                    amount = float(input("Ingrese la cantidad a depositar: "))
                    client_socket.send(f"deposit {account_number} {amount}".encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')
                    print(response)
                    print("----------\n")
                elif choice == "4":
                    receiver_account_number = input("Ingrese el número de cuenta de destino: ")
                    amount = float(input("Ingrese la cantidad a transferir: "))
                    client_socket.send(f"transfer {account_number} {receiver_account_number} {amount}".encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')
                    print(response)
                    print("----------\n")
                elif choice == "5":
                    client_socket.send("exit".encode('utf-8'))
                    break
                else:
                    print("Opción no válida")
                    print("----------\n")

    finally:
        client_socket.close()

if __name__ == '__main__':
    main()
