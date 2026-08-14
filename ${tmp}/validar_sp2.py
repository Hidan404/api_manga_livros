"""Validação do fluxo de autenticação da Sprint 2 (usando TestClient)."""
import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

email = f"sp2{uuid.uuid4().hex[:8]}@email.com"
senha = "123456"

print("=" * 60)
print("1) REGISTER (role deve ser user)")
r = client.post("/auth/register", json={"nome": "Sp2", "email": email, "senha": senha})
print(f"   status={r.status_code} body={r.json()}")

print("\n2) LOGIN (deve retornar tokens e setar cookies)")
r = client.post("/auth/login", json={"email": email, "senha": senha})
print(f"   status={r.status_code}")
data = r.json()
assert "access_token" in data and "refresh_token" in data, data
print(f"   access ok, refresh ok, role={data['role']}")
print(f"   cookies definidos: {[c.name for c in client.cookies.jar]}")

print("\n3) ROTA PROTEGIDA via HEADER Bearer")
r = client.get("/mangas/teste-admin", headers={"Authorization": f"Bearer {data['access_token']}"})
print(f"   status={r.status_code} body={r.json()}")

print("\n4) ROTA PROTEGIDA via COOKIE (access_token)")
client.cookies.clear()
r = client.post("/auth/login", json={"email": email, "senha": senha})  # re-login p/ renovar cookies
data2 = r.json()
r = client.get("/mangas/teste-admin")  # sem header; cookie deve autenticar
print(f"   status={r.status_code} body={r.json()}")

print("\n5) REFRESH via COOKIE (rotação)")
r = client.post("/auth/refresh")
print(f"   status={r.status_code}")
assert r.status_code == 200, r.text
data3 = r.json()
print(f"   novo access + refresh emitidos, role={data3['role']}")
old_refresh = data2["refresh_token"]

print("\n6) REUSO do refresh ANTIGO (deve ser rejeitado e revogar a sessão)")
r = client.post("/auth/refresh", json={"refresh_token": old_refresh})
print(f"   status={r.status_code} detail={r.json().get('detail')}")
assert r.status_code == 401

print("\n7) LOGAUT (revoga refresh e limpa cookies)")
r = client.post("/auth/logout")
print(f"   status={r.status_code} body={r.json()}")
print(f"   cookies restantes: {[c.name for c in client.cookies.jar]}")

print("\n8) ROTAS ADMIN (role=user deve tomar 403)")
r = client.post("/auth/login", json={"email": email, "senha": senha})
token_user = r.json()["access_token"]
r = client.post("/mangas/", headers={"Authorization": f"Bearer {token_user}"},
                json={"titulo": "X", "autor": "Y", "genero": "Z", "status": "S"})
print(f"   criar manga com user: status={r.status_code}")

print("\n9) SEED ADMIN e acesso admin")
from seed_admin import criar_admin  # noqa: E402

criar_admin()
r = client.post("/auth/login", json={"email": "admin@email.com", "senha": "admin123456"})
print(f"   login admin: status={r.status_code}")
token_admin = r.json()["access_token"]
r = client.post("/mangas/", headers={"Authorization": f"Bearer {token_admin}"},
                json={"titulo": "Naruto", "autor": "Kishimoto", "genero": "Shounen", "status": "Completo"})
print(f"   criar manga com admin: status={r.status_code}")

print("\n✅ Validação Sprint 2 concluída")
