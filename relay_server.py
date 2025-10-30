# -*- coding: utf-8 -*-
"""
RELAY SERVER - Merkezi sunucu
Bu sunucu kullanicilar arasinda mesaj iletir
"""
import socket
import threading

clients = {}  # {kod: socket}

def handle_client(client_socket, address):
    print(f"Yeni baglanti: {address}")
    client_code = None
    
    try:
        while True:
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                break
                
            print(f"Gelen: {data[:50]}")
            
            if data.startswith("REGISTER:"):
                client_code = data.split(":")[1]
                clients[client_code] = client_socket
                print(f"Kayit: {client_code}")
                
            elif data.startswith("CONNECT:"):
                target_code = data.split(":")[1]
                if target_code in clients:
                    # Istek gonder
                    clients[target_code].send(f"CONN_REQUEST:{client_code}".encode('utf-8'))
                    print(f"{client_code} -> {target_code} baglanti istegi")
                    
            elif data.startswith("ACCEPT:"):
                target_code = data.split(":")[1]
                if target_code in clients:
                    clients[target_code].send(f"CONN_ACCEPTED:{client_code}".encode('utf-8'))
                    client_socket.send(f"CONN_ACCEPTED:{target_code}".encode('utf-8'))
                    print(f"{client_code} <-> {target_code} baglandi!")
                    
            elif data.startswith("REJECT:"):
                target_code = data.split(":")[1]
                if target_code in clients:
                    clients[target_code].send(b"CONN_REJECTED")
                    print(f"{client_code} -> {target_code} red")
                    
            elif data.startswith("READ:") or data.startswith("WRITE:") or data.startswith("CONTENT:") or data.startswith("ERROR:"):
                # Partnere ilet
                for code, sock in clients.items():
                    if sock != client_socket and code != client_code:
                        try:
                            sock.send(data.encode('utf-8'))
                        except:
                            pass
                            
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        if client_code and client_code in clients:
            del clients[client_code]
        client_socket.close()
        print(f"Baglanti koptu: {address}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 7777))
    server.listen(5)
    
    print("=" * 50)
    print("RELAY SERVER BASLATILDI")
    print("Port: 7777")
    print("Kullanicilar baglanabilir!")
    print("=" * 50)
    
    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client, addr), daemon=True)
        thread.start()

if __name__ == "__main__":
    main()

