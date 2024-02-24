import os
import socket


def listen_udp():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    udp_socket.bind(('0.0.0.0', 4210))
    print("Waiting for incoming packet...")
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
    all_ips = [ip[-1][0] for ip in interfaces]

    msg = b'Hello ESP32'
    for ip in all_ips:
        print(f'Trying to connect from {ip}')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((ip, 4210))
        message_send = False
        if os.path.exists("data/knop.txt"):
            for i in range(3):
                if str(i+1) in open("data/knop.txt", "r").read():
                    sock.sendto(msg, (f"192.168.5.20{i+1}", 4210))
                    print(f"Send to knop {i+1}")
                    message_send = True
        if not message_send:
            sock.sendto(msg, ("255.255.255.255", 4210))
        sock.close()


if __name__ == '__main__':
    listen_udp()
