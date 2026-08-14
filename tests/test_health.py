def test_health(client):
    resposta = client.get("/health")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "ok"
    assert "versao" in corpo
    assert corpo["banco"] == "ok"
