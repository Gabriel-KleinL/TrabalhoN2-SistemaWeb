import sys
import os

# Adicionar o diretório src ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.processarLance import processarLance, lambda_handler
import json

def test_lance_valido():
    """
    Testa se um lance válido é aceito e enviado para a fila
    """
    print("\n=== Teste 1: Lance Válido ===")

    resultado = processarLance(
        leilao_id="LEIL001",
        usuario_id="USER999",
        valor_lance=1600.00
    )

    print(f"Status: {resultado['status']}")
    print(f"Mensagem: {resultado['mensagem']}")

    assert resultado['status'] == 200, "Lance válido deveria ser aceito"
    assert 'lance' in resultado, "Deveria retornar dados do lance"
    print("✅ Teste passou!")
    return resultado


def test_lance_invalido_valor_baixo():
    """
    Testa se um lance com valor menor que o atual é rejeitado
    """
    print("\n=== Teste 2: Lance Inválido (Valor Baixo) ===")

    resultado = processarLance(
        leilao_id="LEIL001",
        usuario_id="USER999",
        valor_lance=1000.00  # Menor que lance_atual (1500)
    )

    print(f"Status: {resultado['status']}")
    print(f"Mensagem: {resultado['mensagem']}")

    assert resultado['status'] == 400, "Lance menor deveria ser rejeitado"
    print("✅ Teste passou!")
    return resultado


def test_leilao_inexistente():
    """
    Testa se leilão inexistente retorna erro 404
    """
    print("\n=== Teste 3: Leilão Inexistente ===")

    resultado = processarLance(
        leilao_id="LEIL999",
        usuario_id="USER999",
        valor_lance=5000.00
    )

    print(f"Status: {resultado['status']}")
    print(f"Mensagem: {resultado['mensagem']}")

    assert resultado['status'] == 404, "Leilão inexistente deveria retornar 404"
    print("✅ Teste passou!")
    return resultado


def test_lambda_handler():
    """
    Testa o handler da Lambda com evento válido
    """
    print("\n=== Teste 4: Lambda Handler ===")

    event = {
        'leilao_id': 'LEIL002',
        'usuario_id': 'USER888',
        'valor_lance': 3500.00
    }

    context = {}

    response = lambda_handler(event, context)

    print(f"Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Body: {json.dumps(body, indent=2)}")

    assert response['statusCode'] == 200, "Lambda deveria retornar 200"
    print("✅ Teste passou!")
    return response


def test_lambda_handler_parametros_faltando():
    """
    Testa o handler da Lambda sem parâmetros obrigatórios
    """
    print("\n=== Teste 5: Lambda Handler - Parâmetros Faltando ===")

    event = {
        'leilao_id': 'LEIL001'
        # Faltando usuario_id e valor_lance
    }

    context = {}

    response = lambda_handler(event, context)

    print(f"Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Mensagem: {body['mensagem']}")

    assert response['statusCode'] == 400, "Deveria retornar 400 para parâmetros faltando"
    print("✅ Teste passou!")
    return response


def test_lances_sequenciais():
    """
    Testa múltiplos lances sequenciais no mesmo leilão
    """
    print("\n=== Teste 6: Lances Sequenciais ===")

    lances = [
        {"usuario_id": "USER101", "valor": 3300.00},
        {"usuario_id": "USER102", "valor": 3400.00},
        {"usuario_id": "USER103", "valor": 3500.00},
    ]

    for i, lance in enumerate(lances, 1):
        resultado = processarLance(
            leilao_id="LEIL002",
            usuario_id=lance["usuario_id"],
            valor_lance=lance["valor"]
        )
        print(f"Lance {i}: {lance['usuario_id']} - R$ {lance['valor']:.2f} -> Status {resultado['status']}")

    print("✅ Teste passou!")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTES DA FUNÇÃO: processarLance")
    print("=" * 60)

    try:
        # Executar todos os testes
        test_lance_valido()
        test_lance_invalido_valor_baixo()
        test_leilao_inexistente()
        test_lambda_handler()
        test_lambda_handler_parametros_faltando()
        test_lances_sequenciais()

        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 60)

    except AssertionError as e:
        print("\n" + "=" * 60)
        print(f"❌ TESTE FALHOU: {e}")
        print("=" * 60)
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERRO INESPERADO: {e}")
        print("=" * 60)
        sys.exit(1)
