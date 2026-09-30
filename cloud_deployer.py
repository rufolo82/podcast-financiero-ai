import base64
import subprocess
import sys
import requests
from nacl import encoding, public
from config import (
    BASE_DIR,
    GEMINI_API_KEY,
    TTS_API_KEY,
    DESTINATION_EMAIL,
    SMTP_USER,
    SMTP_PASSWORD
)

REPO_NAME = "podcast-financiero-ai"

def get_github_credentials() -> tuple[str, str]:
    p = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        text=True,
        capture_output=True
    )
    creds = dict(line.split("=", 1) for line in p.stdout.splitlines() if "=" in line)
    username = creds.get("username", "")
    token = creds.get("password", "")
    if not token:
        raise RuntimeError("No se encontraron credenciales de GitHub en el sistema.")
    return username, token

def encrypt_secret(public_key: str, secret_value: str) -> str:
    public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def deploy_to_github_cloud():
    print("=" * 60)
    print("☁️ SINCRONIZANDO PROYECTO CON LA NUBE (GITHUB ACTIONS)")
    print("=" * 60)

    username, token = get_github_credentials()
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    # 1. Verificar o crear el repositorio
    repo_url = f"https://api.github.com/repos/{username}/{REPO_NAME}"
    r = requests.get(repo_url, headers=headers)
    if r.status_code == 404:
        print(f"📦 Creando repositorio en la nube: {username}/{REPO_NAME}...")
        create_resp = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json={
                "name": REPO_NAME,
                "description": "Podcast Financiero Diario Automatizado (08:00 y 21:00 Madrid)",
                "private": True,
                "auto_init": False
            }
        )
        if create_resp.status_code not in (200, 201):
            raise RuntimeError(f"Error creando repositorio: {create_resp.text}")
        print("✅ Repositorio creado exitosamente.")
    else:
        print(f"✅ Repositorio {username}/{REPO_NAME} detectado.")

    # 2. Subir los Secrets encriptados a GitHub Actions
    print("🔐 Configurando claves seguras (Secrets) en GitHub Actions...")
    pk_resp = requests.get(f"{repo_url}/actions/secrets/public-key", headers=headers)
    if pk_resp.status_code != 200:
        raise RuntimeError(f"Error obteniendo clave pública de Actions: {pk_resp.text}")
    pk_data = pk_resp.json()
    key_id = pk_data["key_id"]
    pub_key = pk_data["key"]

    secrets_to_upload = {
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "TTS_API_KEY": TTS_API_KEY,
        "DESTINATION_EMAIL": DESTINATION_EMAIL,
        "SMTP_USER": SMTP_USER,
        "SMTP_PASSWORD": SMTP_PASSWORD
    }

    for s_name, s_val in secrets_to_upload.items():
        if not s_val:
            continue
        enc_val = encrypt_secret(pub_key, s_val)
        s_resp = requests.put(
            f"{repo_url}/actions/secrets/{s_name}",
            headers=headers,
            json={
                "encrypted_value": enc_val,
                "key_id": key_id
            }
        )
        if s_resp.status_code in (201, 204):
            print(f"   • Secret '{s_name}' actualizado.")
        else:
            print(f"   ⚠️ Error en '{s_name}': {s_resp.text}")

    # 3. Sincronizar código vía Git
    print("📤 Subiendo archivos del proyecto a la nube...")
    remote_url = f"https://github.com/{username}/{REPO_NAME}.git"
    
    if not (BASE_DIR / ".git").exists():
        subprocess.run(["git", "init"], cwd=BASE_DIR, check=True, capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=BASE_DIR, check=True, capture_output=True)

    # Configurar remoto
    remotes = subprocess.run(["git", "remote"], cwd=BASE_DIR, capture_output=True, text=True).stdout.splitlines()
    if "origin" in remotes:
        subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=BASE_DIR, check=True)
    else:
        subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=BASE_DIR, check=True)

    subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, capture_output=True, text=True).stdout.strip()
    if status:
        subprocess.run(["git", "commit", "-m", "Sincronización automática Podcast Financiero"], cwd=BASE_DIR, check=True, capture_output=True)
    
    push_res = subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=BASE_DIR, capture_output=True, text=True)
    if push_res.returncode != 0:
        raise RuntimeError(f"Error en git push: {push_res.stderr}")

    print(f"✅ Código sincronizado en: https://github.com/{username}/{REPO_NAME}")
    print("🎉 El podcast ahora se ejecutará en la nube a las 08:00 y 21:00 incluso con el PC apagado.")
    print("=" * 60)

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    deploy_to_github_cloud()
