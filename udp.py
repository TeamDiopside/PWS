import socket


def listen_udp():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    udp_socket.bind(('0.0.0.0', 4210))  # Example IP and port
    print("UDP server is running. Waiting for incoming packets...")
    data, addr = udp_socket.recvfrom(1024)
    print(f"Received packet from {addr}: {data.decode()}")
    udp_socket.close()
    if data == b'PUSH':
        open("data/button_integration_data", 'w').writelines("true")
    if data == b'BROADCAST':
        broadcast()

    listen_udp()


def broadcast():
    interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
    allips = [ip[-1][0] for ip in interfaces]

    msg = b'Hello ESP32'
    for ip in allips:
        print(f'sending on {ip}')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((ip, 4210))
        sock.sendto(msg, ("255.255.255.255", 4210))
        sock.close()


if __name__ == '__main__':
    listen_udp()
