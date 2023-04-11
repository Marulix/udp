from datetime import datetime
import os
import socket
import threading
import time

MAX_PACKET_SIZE = 2048
lock = threading.Lock()

def log(cliente, tiempo, nombreLog, tamanio_final, exito):
    texto = ["Conexión del cliente {} \n Tiempo de transferencia: {}s \n Tamaño final: {}MB \n Éxito: {}\n".format(cliente, tiempo, tamanio_final, exito) ]
    lock.acquire()
    with open("Logs/" + nombreLog, "a") as f:
        f.writelines(texto)
        f.close()
    lock.release() 

def client(filename, request, nombre_log, num_cliente):
    udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_client_socket.settimeout(10)
    server_address = ('192.168.89.131', 12345)
    udp_client_socket.sendto(request.encode(), server_address)

    if not os.path.exists("Archivos Recibidos"):
        os.makedirs("Archivos Recibidos")
    file = open("Archivos Recibidos\ ".strip() + filename, 'wb')

    start = time.time()
    success = True
    while True:
        try:
            data, server_address = udp_client_socket.recvfrom(MAX_PACKET_SIZE)
        except socket.timeout:
            success = False
            file.close()
            break
        file.write(data)
        if not data or len(data) < MAX_PACKET_SIZE:
            file.close()
            break
    end = time.time()
    tiempo = end - start
    print('File received from {}:{}'.format(server_address[0], server_address[1]))
    tamanio_final = int(os.path.getsize("Archivos Recibidos\ ".strip() + filename))/1000000
    log(num_cliente, round(tiempo, 2), nombre_log, tamanio_final, success)
    udp_client_socket.close()


def main():
    print("Bienvenido al cliente de archivos \n Escoja el tamaño de archivo que desea enviar: \n 1. 100MB \n 2. 250MB")
    opcion = input("Ingrese el numero de la opcion: ")
    if opcion == "1":
        request = '100MB'
        filename = 'prueba100.txt'
    elif opcion == "2":
        request = '250MB'
        filename = 'prueba250.txt'
    else:
        print("Opcion no valida")
        exit()

    numClientes = int(input("Ingrese el numero de clientes: "))

    tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('192.168.89.131', 12345)
    tcp_client_socket.connect(server_address)

    tcp_client_socket.send((request + " " + str(numClientes)).encode())


    tcp_client_socket.close()


    nombreLog = datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".txt"
    texto = ["Archivo recibido: " + filename + "\n"]
    if not os.path.exists("Logs"):
        os.makedirs("Logs")
    with open("Logs/"+nombreLog, "w") as f:
        f.writelines(texto)
        f.close()
        
    for i in range(1, numClientes+1):
        nombre = f"Cliente{i}-Prueba-{numClientes}.txt"
        thread = threading.Thread(target=client, args=(nombre, request, nombreLog, i))
        thread.start()


if __name__ == "__main__":
    main()




