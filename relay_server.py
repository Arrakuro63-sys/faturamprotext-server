# -*- coding: utf-8 -*-
"""
RELAY SERVER - Flask + Socket.IO (Render uyumlu)
"""
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'faturampro-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Clients: {code: sid}
clients = {}
# SID to Code mapping
sid_to_code = {}

@app.route('/')
def index():
    return '''
    <h1>FaturamProText Relay Server</h1>
    <p>Server is running!</p>
    <p>Status: <span style="color:green">ONLINE</span></p>
    '''

@app.route('/health')
def health():
    return {'status': 'ok', 'clients': len(clients)}

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    
@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in sid_to_code:
        code = sid_to_code[sid]
        if code in clients:
            del clients[code]
        del sid_to_code[sid]
        print(f'Client disconnected: {sid} (code: {code})')
    
@socketio.on('register')
def handle_register(data):
    code = data.get('code')
    sid = request.sid
    
    clients[code] = sid
    sid_to_code[sid] = code
    print(f'Registered: {code} -> {sid}')
    emit('registered', {'code': code})
    
@socketio.on('connect_to')
def handle_connect_to(data):
    target_code = data.get('code')
    sender_code = sid_to_code.get(request.sid)
    
    if target_code in clients:
        target_sid = clients[target_code]
        emit('connection_request', {'code': sender_code}, room=target_sid)
        print(f'{sender_code} -> {target_code}: connection request')
    
@socketio.on('accept')
def handle_accept(data):
    target_code = data.get('code')
    sender_code = sid_to_code.get(request.sid)
    
    if target_code in clients:
        target_sid = clients[target_code]
        emit('connection_accepted', {'code': sender_code}, room=target_sid)
        emit('connection_accepted', {'code': target_code})
        print(f'{sender_code} <-> {target_code}: connected')
    
@socketio.on('reject')
def handle_reject(data):
    target_code = data.get('code')
    sender_code = sid_to_code.get(request.sid)
    
    if target_code in clients:
        target_sid = clients[target_code]
        emit('connection_rejected', {}, room=target_sid)
        print(f'{sender_code} -> {target_code}: rejected')
    
@socketio.on('relay')
def handle_relay(data):
    sender_code = sid_to_code.get(request.sid)
    target_code = data.get('target')
    message = data.get('message')
    
    if target_code and target_code in clients:
        target_sid = clients[target_code]
        emit('relay', {'message': message, 'from': sender_code}, room=target_sid)

if __name__ == '__main__':
    from flask import request
    port = int(os.environ.get('PORT', 5555))
    print("=" * 50)
    print("RELAY SERVER BASLATILDI (Flask + Socket.IO)")
    print(f"Port: {port}")
    print("=" * 50)
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)

