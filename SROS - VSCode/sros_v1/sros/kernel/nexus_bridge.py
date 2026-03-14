"""
Nexus Bridge
============

Zero-Dependency WebSocket Server for SROS Nexus.
Bridges the SROS Kernel EventBus to the Web UI.
"""
import socket
import threading
import hashlib
import base64
import struct
import json
import logging
import time
from typing import List

logger = logging.getLogger(__name__)

class NexusBridge:
    """
    A lightweight, zero-dependency WebSocket server.
    """
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients: List[socket.socket] = []
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        """Start the WebSocket server in a background thread."""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            logger.info(f"Nexus Bridge listening on ws://{self.host}:{self.port}")
            
            threading.Thread(target=self._accept_loop, daemon=True).start()
        except Exception as e:
            logger.error(f"Failed to start Nexus Bridge: {e}")

    def stop(self):
        """Stop the server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        with self.lock:
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()

    def broadcast(self, message: dict):
        """Broadcast a JSON message to all connected clients."""
        payload = json.dumps(message)
        frame = self._make_frame(payload)
        
        with self.lock:
            to_remove = []
            for client in self.clients:
                try:
                    client.sendall(frame)
                except Exception:
                    to_remove.append(client)
            
            for client in to_remove:
                self.clients.remove(client)

    def _accept_loop(self):
        """Accept incoming connections."""
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
                logger.info(f"Nexus Client connected: {addr}")
                threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True).start()
            except Exception:
                if self.running:
                    logger.exception("Accept error")
                break

    def _handle_client(self, client_sock):
        """Handle the WebSocket handshake and connection."""
        try:
            data = client_sock.recv(1024)
            if not data:
                client_sock.close()
                return

            headers = self._parse_headers(data.decode('utf-8', errors='ignore'))
            if 'Sec-WebSocket-Key' not in headers:
                client_sock.close()
                return

            # Handshake
            key = headers['Sec-WebSocket-Key']
            accept_key = self._generate_accept_key(key)
            response = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept_key}\r\n\r\n"
            )
            client_sock.sendall(response.encode('utf-8'))
            
            with self.lock:
                self.clients.append(client_sock)
                
            # Keep alive / Read loop (Nexus is mostly receive-only for now)
            while self.running:
                data = client_sock.recv(1024)
                if not data:
                    break
                # We ignore incoming frames for now, just a bridge out.
        except Exception:
            pass
        finally:
            with self.lock:
                if client_sock in self.clients:
                    self.clients.remove(client_sock)
            client_sock.close()

    def _parse_headers(self, request):
        headers = {}
        lines = request.split('\r\n')
        for line in lines[1:]:
            if ': ' in line:
                key, value = line.split(': ', 1)
                headers[key] = value
        return headers

    def _generate_accept_key(self, key):
        guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        sha1 = hashlib.sha1((key + guid).encode('utf-8')).digest()
        return base64.b64encode(sha1).decode('utf-8')

    def _make_frame(self, payload):
        """Construct a WebSocket frame."""
        payload_bytes = payload.encode('utf-8')
        length = len(payload_bytes)
        frame = bytearray()
        frame.append(0x81) # Text frame, FIN bit set

        if length <= 125:
            frame.append(length)
        elif length <= 65535:
            frame.append(126)
            frame.extend(struct.pack("!H", length))
        else:
            frame.append(127)
            frame.extend(struct.pack("!Q", length))

        frame.extend(payload_bytes)
        return frame
