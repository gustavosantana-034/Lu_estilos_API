import pytest
from schemas.client import ClientBase

def test_cpf_valid():
    cliente = ClientBase(
        name="João",
        email="joao@example.com",
        cpf="123.456.789-09",  # cpf válido ou inválido para testar
        phone="11999999999"
    )
    assert cliente.cpf == "123.456.789-09"  # ou a versão formatada correta

def test_cpf_invalid():
    import pytest
    with pytest.raises(ValueError):
        ClientBase(
            name="Maria",
            email="maria@example.com",
            cpf="111.111.111-11",  # cpf inválido
            phone="11999999999"
        )
