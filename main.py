from fastapi import FastAPI, Security, HTTPException
from fastapi.security import APIKeyHeader
import uvicorn
import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración SSH
SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = os.getenv("SSH_PORT")
SSH_USER = os.getenv("SSH_USER")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")

# Configuración API
API_TOKEN = os.getenv("API_TOKEN")
API_TOKEN_NAME = os.getenv("API_TOKEN_NAME")

app = FastAPI()
api_key_header = APIKeyHeader(name=API_TOKEN_NAME, auto_error=False)

def execute_ssh_command(command: str):
    """Ejecuta un comando remoto vía SSH"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=SSH_HOST,
            port=SSH_PORT,
            username=SSH_USER,
            password=SSH_PASSWORD,
            timeout=10
        )
        stdin, stdout, stderr = client.exec_command(command)
        return {
            "output": stdout.read().decode(),
            "error": stderr.read().decode(),
            "status": stdout.channel.recv_exit_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        client.close()

async def validate_token(api_key: str = Security(api_key_header)):
    if api_key != API_TOKEN:
        raise HTTPException(status_code=403, detail="Token inválido")
    return True

@app.get("/ssh-test")
async def test_ssh_connection(auth: bool = Security(validate_token)):
    """Prueba de conexión SSH básica"""
    result = execute_ssh_command("hostname && uptime")
    return {
        "ssh_status": "success" if result["status"] == 0 else "error",
        "output": result["output"],
        "server": SSH_HOST
    }

@app.get("/port-check")
async def check_port(auth: bool = Security(validate_token)):
    """Verifica el puerto SSH desde dentro del servidor"""
    result = execute_ssh_command(f"netstat -tuln | grep :7878")
    return {
        "port_7878_status": "open" if ":7878" in result["output"] else "closed",
        "details": result["output"]
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7878,
        reload=False,
        access_log=True
    )
