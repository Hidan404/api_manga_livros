from app.utils.jwt_gerenciador import Autenticacao_config

jwtm = Autenticacao_config()

token = jwtm.create_access_token(user_id=10)
print("Access Token:", token)

payload = jwtm.decode_token(token)
print("Payload:", payload)
