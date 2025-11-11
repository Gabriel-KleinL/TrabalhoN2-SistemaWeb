import sys
import os
import json

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importar as funções - agora funciona com imports relativos
if __name__ == "__main__":
    # Quando executado diretamente, importar de forma absoluta
    from src.finalizarLeilao import finalizarLeilao, lambda_handler
    from src.processarLance import processarLance
else:
    # Quando executado via pytest, usar imports relativos
    from src.finalizarLeilao import finalizarLeilao, lambda_handler
    from src.processarLance import processarLance

def test_finalizar_leilao_basico():
    """
    Testa finalização básica de um leilão
    """
    print("\n=== Teste 1: Finalizar Leilão Básico ===")

    resultado = finalizarLeilao(leilao_id="LEIL001")

    print(f"Status: {resultado['status']}")
    print(f"Mensagem: {resultado['mensagem']}")

    if resultado['status'] == 200:
        res = resultado['resultado']
        print(f"Leilão: {res['titulo']}")
        print(f"Lance inicial: R$ {res['lance_inicial']:.2f}")
        print(f"Lance vencedor: R$ {res['lance_vencedor']:.2f}")
        print(f"Vencedor: {res['usuario_vencedor']}")
        print(f"Total de lances: {res['total_lances']}")
        print(f"Incremento: {res['incremento_percentual']}%")

    assert resultado['status'] == 200, "Finalização deveria ser bem-sucedida"
    assert 'resultado' in resultado, "Deveria retornar resultado"
    print("✅ Teste passou!")
    return resultado


def test_finalizar_leilao_inexistente():
    """
    Testa finalização de leilão que não existe
    """
    print("\n=== Teste 2: Finalizar Leilão Inexistente ===")

    resultado = finalizarLeilao(leilao_id="LEIL999")

    print(f"Status: {resultado['status']}")
    print(f"Mensagem: {resultado['mensagem']}")

    assert resultado['status'] == 404, "Deveria retornar 404 para leilão inexistente"
    print("✅ Teste passou!")
    return resultado


def test_lambda_handler():
    """
    Testa o handler da Lambda
    """
    print("\n=== Teste 3: Lambda Handler ===")

    event = {
        'leilao_id': 'LEIL002'
    }

    context = {}

    response = lambda_handler(event, context)

    print(f"Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Mensagem: {body['mensagem']}")

    if response['statusCode'] == 200:
        res = body['resultado']
        print(f"Vencedor: {res['usuario_vencedor']}")
        print(f"Lance vencedor: R$ {res['lance_vencedor']:.2f}")

    assert response['statusCode'] in [200, 400], "Lambda deveria retornar status válido"
    print("✅ Teste passou!")
    return response


def test_lambda_handler_sem_parametros():
    """
    Testa handler sem parâmetro obrigatório
    """
    print("\n=== Teste 4: Lambda Handler Sem Parâmetros ===")

    event = {}
    context = {}

    response = lambda_handler(event, context)

    print(f"Status Code: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Mensagem: {body['mensagem']}")

    assert response['statusCode'] == 400, "Deveria retornar 400 sem parâmetros"
    print("✅ Teste passou!")
    return response


def test_finalizar_com_lances_na_fila():
    """
    Testa finalização após adicionar lances na fila
    """
    print("\n=== Teste 5: Finalizar com Lances na Fila ===")

    # Adicionar alguns lances na fila
    print("Adicionando lances à fila...")
    processarLance("LEIL003", "USER201", 2600.00)
    processarLance("LEIL003", "USER202", 2700.00)
    processarLance("LEIL003", "USER203", 2800.00)

    # Finalizar leilão
    resultado = finalizarLeilao(leilao_id="LEIL003")

    print(f"Status: {resultado['status']}")
    print(f"Mensagem: {resultado['mensagem']}")

    if resultado['status'] == 200:
        res = resultado['resultado']
        print(f"Título: {res['titulo']}")
        print(f"Lance vencedor: R$ {res['lance_vencedor']:.2f}")
        print(f"Vencedor: {res['usuario_vencedor']}")
        print(f"Total de lances: {res['total_lances']}")

        # O lance vencedor deveria ser o maior (2800)
        assert res['lance_vencedor'] >= 2800.00, "Lance vencedor deveria ser >= R$ 2800"
        assert res['total_lances'] >= 5, "Deveria ter pelo menos 5 lances (2 históricos + 3 da fila)"

    print("✅ Teste passou!")
    return resultado


def test_comparar_multiplos_leiloes():
    """
    Testa finalização de múltiplos leilões
    """
    print("\n=== Teste 6: Comparar Múltiplos Leilões ===")

    leiloes = ["LEIL001", "LEIL002", "LEIL003"]

    for leilao_id in leiloes:
        resultado = finalizarLeilao(leilao_id=leilao_id)

        if resultado['status'] == 200:
            res = resultado['resultado']
            print(f"\n{leilao_id} - {res['titulo']}")
            print(f"  Lance vencedor: R$ {res['lance_vencedor']:.2f}")
            print(f"  Incremento: {res['incremento_percentual']}%")
        else:
            print(f"\n{leilao_id} - {resultado['mensagem']}")

    print("✅ Teste passou!")


def test_validar_dados_vencedor():
    """
    Testa se os dados do vencedor são válidos
    """
    print("\n=== Teste 7: Validar Dados do Vencedor ===")

    resultado = finalizarLeilao(leilao_id="LEIL001")

    if resultado['status'] == 200:
        res = resultado['resultado']

        # Validações
        assert res['lance_vencedor'] >= res['lance_inicial'], "Lance vencedor deve ser >= lance inicial"
        assert res['usuario_vencedor'] is not None, "Deve ter um usuário vencedor"
        assert res['total_lances'] > 0, "Deve ter pelo menos 1 lance"
        assert res['incremento_percentual'] >= 0, "Incremento deve ser >= 0"

        print(f"Lance inicial: R$ {res['lance_inicial']:.2f}")
        print(f"Lance vencedor: R$ {res['lance_vencedor']:.2f}")
        print(f"Incremento: {res['incremento_percentual']}%")
        print("✅ Todos os dados são válidos!")
    else:
        print(f"Aviso: {resultado['mensagem']}")

    print("✅ Teste passou!")
    return resultado


if __name__ == "__main__":
    print("=" * 60)
    print("TESTES DA FUNÇÃO: finalizarLeilao")
    print("=" * 60)

    try:
        # Executar todos os testes
        test_finalizar_leilao_basico()
        test_finalizar_leilao_inexistente()
        test_lambda_handler()
        test_lambda_handler_sem_parametros()
        test_finalizar_com_lances_na_fila()
        test_comparar_multiplos_leiloes()
        test_validar_dados_vencedor()

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
        import traceback
        traceback.print_exc()
        sys.exit(1)
