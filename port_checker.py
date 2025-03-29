import socket
import os
from dotenv import load_dotenv

load_dotenv()

def check_port(host: str, port: int, timeout=3):
    """Verifica si un puerto está accesible"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))
            return True
    except:
        return False

if __name__ == "__main__":
    SERVER_IP = os.getenv("SERVER_IP", "192.46.223.247")
    PORT = int(os.getenv("PORT", 7878))

    if check_port(SERVER_IP, PORT):
        print(f"✅ Puerto {PORT} accesible en {SERVER_IP}")
    else:
        print(f"❌ Puerto {PORT} bloqueado en {SERVER_IP}")
