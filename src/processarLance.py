from .filaLances import filaLances
import json
from datetime import datetime

def processarLance(leilao_id, usuario_id, valor_lance):
    '''
    Processa um novo lance em um leilao.
    Valida se o lance e maior que o lance atual e envia para a fila.
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

        # Validar status do leilao
        if leilao_encontrado["status"] != "ativo":
            return {"status": 400,
                    "mensagem": "Leilao nao esta ativo!"}

        # Validar se o lance e maior que o lance atual
        if valor_lance <= leilao_encontrado["lance_atual"]:
            return {"status": 400,
                    "mensagem": f"Lance deve ser maior que R$ {leilao_encontrado['lance_atual']:.2f}"}

        # Criar objeto do lance
        lance = {
            "leilao_id": leilao_id,
            "usuario_id": usuario_id,
            "valor": valor_lance,
            "data_hora": datetime.now().isoformat(),
            "status": "pendente",
            "leilao_titulo": leilao_encontrado["titulo"]
        }

        # Enviar lance para a fila
        filaLances.put(lance)

        return {"status": 200,
                "mensagem": "Lance recebido e enviado para processamento!",
                "lance": lance}

    except KeyError as e:
        return {"status": 500,
                "mensagem": f"Erro ao processar dados: campo {str(e)} nao encontrado!"}
    except Exception as e:
        return {"status": 500,
                "mensagem": f"Erro ao processar lance: {str(e)}"}


# Funcao handler para AWS Lambda
def lambda_handler(event, context):
    '''
    Handler principal para AWS Lambda.
    '''
    try:
        leilao_id = event.get('leilao_id')
        usuario_id = event.get('usuario_id')
        valor_lance = event.get('valor_lance')

        if not all([leilao_id, usuario_id, valor_lance]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'mensagem': 'Parametros obrigatorios: leilao_id, usuario_id, valor_lance'
                })
            }

        resultado = processarLance(leilao_id, usuario_id, float(valor_lance))

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
