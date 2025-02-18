from datetime import datetime
import socket
import os
import threading
import time
import hashlib

MAX_PACKET_SIZE = 2048
lock = threading.Lock()


def log(cliente, tiempo, nombreLog):
    texto = ["Conexión del cliente {} \n Tiempo de transferencia: {}s\n".format(cliente, tiempo) ]
    lock.acquire()
    with open("Logs/" + nombreLog, "a") as f:
        f.writelines(texto)
        f.close()
    lock.release()  


def handle_client_request(client_address, filename, num_cliente, nombreLog):
    file = open(filename, 'rb')
    start = time.time()
    while True:
        file_data = file.read(MAX_PACKET_SIZE)

        if not file_data:
            break

        sent = 0
        while sent < len(file_data):
            packet = file_data[sent:sent + MAX_PACKET_SIZE]
            server_socket.sendto(packet, client_address)
            sent += MAX_PACKET_SIZE
    end = time.time()
    tiempo = end - start
    log(num_cliente, round(tiempo, 2), nombreLog)

    print('File sent to {}:{}'.format(client_address[0], client_address[1]))
    file.close()

def main():
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_address = ('192.168.89.131', 12345)
    tcp_server_socket.bind(tcp_server_address)
    tcp_server_socket.listen()

    print('TCP server is listening on {}:{}'.format(tcp_server_address[0], tcp_server_address[1]))
    tcp_client_socket, tcp_client_address = tcp_server_socket.accept()

    data = tcp_client_socket.recv(MAX_PACKET_SIZE)
    if '100MB' in data.decode():
        filename = 'prueba100.txt'
        tcp_client_socket.send('File exists'.encode())
    elif '250MB' in data.decode():
        filename = 'prueba250.txt'
        tcp_client_socket.send('File exists'.encode())
    else:
        tcp_client_socket.close()
        return

    numClientes = int(data.decode().split()[1])
    tcp_client_socket.close()

    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('192.168.89.131', 12345)
    server_socket.bind(server_address)

    print('UDP server is listening on {}:{}'.format(server_address[0], server_address[1]))

    nombreLog = datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".txt"
    texto = ["Archivo enviado: " + filename + "\n", "Tamaño del archivo: " + str(int((os.path.getsize(filename)))/1000000) + "MB\n"]
    if not os.path.exists("Logs"):
        os.makedirs("Logs")
    with open("Logs/"+nombreLog, "w") as f:
        f.writelines(texto)
        f.close()

    threads = []
    for i in range(1, numClientes+1):
        data, client_address = server_socket.recvfrom(MAX_PACKET_SIZE)
        thread = threading.Thread(target=handle_client_request, args=(client_address, filename, i, nombreLog))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    server_socket.close()

if __name__ == '__main__':
    main()
