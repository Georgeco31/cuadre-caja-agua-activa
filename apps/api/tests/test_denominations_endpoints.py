def test_denominations_endpoint_returns_list(api_client, api_denominations) -> None:
    client, _ = api_client

    response = client.get("/api/v1/denominations")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 4
    assert {item["label"] for item in body} == {
        "Moneda de 25 centavos",
        "Moneda de 1 dolar",
        "Billete de 10 dolares",
        "Billete de 20 dolares",
    }
    assert all(item["is_active"] is True for item in body)
