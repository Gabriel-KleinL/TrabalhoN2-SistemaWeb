from .filaLances import filaLances
import json
from datetime import datetime

def finalizarLeilao(leilao_id):
    '''
    Finaliza um leilao, processa os lances da fila e determina o vencedor.
    '''
    try:
        # Buscar dados do leilao
        arq = open("./schema/cadastroLeilao.json", "r")
        dadosLeiloes = json.loads(arq.read())
        arq.close()

        leilao_encontrado = None
        for leilao in dadosLeiloes['leiloes']:
            if leilao["id"] == leilao_id:
                leilao_encontrado = leilao
                break

        if leilao_encontrado is None:
            return {"status": 404,
                    "mensagem": "Leilao nao encontrado!"}

        # Buscar todos os lances do leilao
        arq = open("./schema/cadastroLance.json", "r")
        dadosLances = json.loads(arq.read())
        arq.close()

        # Filtrar lances do leilao especifico
        lances_do_leilao = [
            lance for lance in dadosLances['lances']
            if lance['leilao_id'] == leilao_id and lance['status'] == 'aceito'
        ]

        # Processar lances da fila (se houver)
        lances_fila = []
        while not filaLances.empty():
            lance_fila = filaLances.get()
            if lance_fila['leilao_id'] == leilao_id:
                lances_fila.append(lance_fila)

        # Combinar todos os lances
        todos_lances = lances_do_leilao + lances_fila

        if not todos_lances:
            return {"status": 400,
                    "mensagem": "Nenhum lance encontrado para este leilao!"}

        # Determinar o lance vencedor (maior valor)
        lance_vencedor = max(todos_lances, key=lambda x: x['valor'])

        # Atualizar status do leilao
        leilao_encontrado['status'] = 'finalizado'
        leilao_encontrado['lance_vencedor'] = lance_vencedor['valor']
        leilao_encontrado['usuario_vencedor'] = lance_vencedor['usuario_id']
        leilao_encontrado['data_finalizacao'] = datetime.now().isoformat()

        # Salvar atualizacao (simulado - em producao salvaria no banco)
        for i, leilao in enumerate(dadosLeiloes['leiloes']):
            if leilao['id'] == leilao_id:
                dadosLeiloes['leiloes'][i] = leilao_encontrado
                break

        # Estatisticas
        total_lances = len(todos_lances)
        valor_inicial = leilao_encontrado['lance_inicial']
        valor_final = lance_vencedor['valor']
        incremento_percentual = ((valor_final - valor_inicial) / valor_inicial) * 100

        return {
            "status": 200,
            "mensagem": "Leilao finalizado com sucesso!",
            "resultado": {
                "leilao_id": leilao_id,
                "titulo": leilao_encontrado['titulo'],
                "lance_inicial": valor_inicial,
                "lance_vencedor": valor_final,
                "usuario_vencedor": lance_vencedor['usuario_id'],
                "total_lances": total_lances,
                "incremento_percentual": round(incremento_percentual, 2),
                "data_finalizacao": leilao_encontrado['data_finalizacao']
            }
        }

    except KeyError as e:
        return {"status": 500,
                "mensagem": f"Erro ao processar dados: campo {str(e)} nao encontrado!"}
    except Exception as e:
        return {"status": 500,
                "mensagem": f"Erro ao finalizar leilao: {str(e)}"}


# Funcao handler para AWS Lambda
def lambda_handler(event, context):
    '''
    Handler principal para AWS Lambda.
    '''
    try:
        leilao_id = event.get('leilao_id')

        if not leilao_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'mensagem': 'Parametro obrigatorio: leilao_id'
                })
            }

        resultado = finalizarLeilao(leilao_id)

        return {
            'statusCode': resultado['status'],
            'body': json.dumps(resultado)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'mensagem': f'Erro interno: {str(e)}'
            })
        }
