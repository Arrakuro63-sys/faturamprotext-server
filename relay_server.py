# -*- coding: utf-8 -*-
"""
RELAY SERVER - WebSocket ile (HTTP uyumlu)
Bu sunucu kullanicilar arasinda mesaj iletir
"""
import asyncio
import websockets
import json
import os

clients = {}  # {kod: websocket}

async def handle_client(websocket, path):
    client_code = None
    print(f"Yeni baglanti: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            data = message
            print(f"Gelen: {data[:50]}")
            
            if data.startswith("REGISTER:"):
                client_code = data.split(":")[1]
                clients[client_code] = websocket
                print(f"Kayit: {client_code}")
                
            elif data.startswith("CONNECT:"):
                target_code = data.split(":")[1]
                if target_code in clients:
                    await clients[target_code].send(f"CONN_REQUEST:{client_code}")
                    print(f"{client_code} -> {target_code} baglanti istegi")
                    
            elif data.startswith("ACCEPT:"):
                target_code = data.split(":")[1]
                if target_code in clients:
                    await clients[target_code].send(f"CONN_ACCEPTED:{client_code}")
                    await websocket.send(f"CONN_ACCEPTED:{target_code}")
                    print(f"{client_code} <-> {target_code} baglandi!")
                    
            elif data.startswith("REJECT:"):
                target_code = data.split(":")[1]
                if target_code in clients:
                    await clients[target_code].send("CONN_REJECTED")
                    print(f"{client_code} -> {target_code} red")
                    
            elif data.startswith("READ:") or data.startswith("WRITE:") or data.startswith("CONTENT:") or data.startswith("ERROR:"):
                # Partnere ilet
                for code, sock in clients.items():
                    if sock != websocket and code != client_code:
                        try:
                            await sock.send(data)
                        except:
                            pass
                            
    except websockets.exceptions.ConnectionClosed:
        print(f"Baglanti koptu: {websocket.remote_address}")
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        if client_code and client_code in clients:
            del clients[client_code]
        print(f"Temizlendi: {client_code}")

async def main():
    # Render PORT'u al, yoksa 5555 kullan
    port = int(os.environ.get('PORT', 5555))
    
    print("=" * 50)
    print("RELAY SERVER BASLATILDI (WebSocket)")
    print(f"Port: {port}")
    print("Kullanicilar baglanabilir!")
    print("=" * 50)
    
    async with websockets.serve(handle_client, "0.0.0.0", port):
        await asyncio.Future()  # Sonsuz bekle

if __name__ == "__main__":
    asyncio.run(main())

