# Sistema de Leilão Online

## 📋 Descrição

Sistema de leilão online desenvolvido com arquitetura serverless utilizando AWS Lambda e filas para processamento assíncrono de lances. O sistema permite que usuários façam lances em produtos e determina automaticamente o vencedor ao finalizar o leilão.

---

## 🏗️ Arquitetura

O sistema foi desenvolvido seguindo os requisitos da avaliação:
- ✅ **2 Lambdas** (funções serverless)
- ✅ **1 Fila** (processamento assíncrono)

### Diagrama da Arquitetura

```
Cliente (API Gateway)
        ↓
Lambda 1: processarLance
   - Valida lance
   - Envia para fila
        ↓
   filaLances (Queue)
        ↓
Lambda 2: finalizarLeilao
   - Processa lances
   - Determina vencedor
```

---

## 📁 Estrutura do Projeto

```
TrabalhoN2-SistemaWeb/
│
├── README.md                   # Este arquivo
│
├── docs/
│   ├── README.md               # Documentação técnica detalhada
│   └── arquitetura.png         # Diagrama visual da arquitetura
│
├── schema/
│   ├── cadastroLeilao.json     # Base de dados de leilões
│   └── cadastroLance.json      # Histórico de lances
│
└── src/
    ├── filaLances.py           # Fila para processamento de lances
    ├── processarLance.py       # Lambda 1: Recebe e valida lances
    └── finalizarLeilao.py      # Lambda 2: Finaliza leilão e determina vencedor
```

---

## 🔧 Componentes

### 1. Lambda 1: processarLance

**Arquivo:** `src/processarLance.py`

**Responsabilidades:**
- Receber lance do usuário
- Validar se o leilão existe e está ativo
- Verificar se o lance é maior que o lance atual
- Enviar lance para a fila de processamento

**Entrada (event):**
```json
{
  "leilao_id": "LEIL001",
  "usuario_id": "USER101",
  "valor_lance": 1600.00
}
```

**Saída:**
```json
{
  "status": 200,
  "mensagem": "Lance recebido e enviado para processamento!",
  "lance": {
    "leilao_id": "LEIL001",
    "usuario_id": "USER101",
    "valor": 1600.00,
    "data_hora": "2025-11-10T14:30:00",
    "status": "pendente"
  }
}
```

---

### 2. Fila: filaLances

**Arquivo:** `src/filaLances.py`

**Tipo:** `queue.Queue()` (Python)

**Função:**
- Armazenar lances temporariamente
- Permitir processamento assíncrono
- Desacoplar recepção de processamento

---

### 3. Lambda 2: finalizarLeilao

**Arquivo:** `src/finalizarLeilao.py`

**Responsabilidades:**
- Processar todos os lances da fila
- Buscar lances históricos do banco de dados
- Determinar o lance vencedor (maior valor)
- Calcular estatísticas do leilão
- Finalizar o leilão

**Entrada (event):**
```json
{
  "leilao_id": "LEIL001"
}
```

**Saída:**
```json
{
  "status": 200,
  "mensagem": "Leilao finalizado com sucesso!",
  "resultado": {
    "leilao_id": "LEIL001",
    "titulo": "Notebook Dell Inspiron 15",
    "lance_inicial": 1500.00,
    "lance_vencedor": 2000.00,
    "usuario_vencedor": "USER105",
    "total_lances": 8,
    "incremento_percentual": 33.33,
    "data_finalizacao": "2025-11-10T18:00:00"
  }
}
```

---

## 📊 Schemas (Banco de Dados)

### cadastroLeilao.json

Estrutura dos leilões:
```json
{
  "id": "LEIL001",
  "titulo": "Notebook Dell Inspiron 15",
  "descricao": "Notebook em excelente estado...",
  "lance_inicial": 1500.00,
  "lance_atual": 1500.00,
  "data_inicio": "2025-11-10T08:00:00",
  "data_fim": "2025-11-15T18:00:00",
  "status": "ativo",
  "vendedor_id": "USER001"
}
```

**Campos:**
- `id`: Identificador único do leilão
- `titulo`: Nome do produto
- `descricao`: Descrição detalhada
- `lance_inicial`: Valor inicial do leilão
- `lance_atual`: Maior lance atual
- `data_inicio/data_fim`: Período do leilão
- `status`: ativo/finalizado
- `vendedor_id`: ID do vendedor

---

### cadastroLance.json

Histórico de lances:
```json
{
  "id": "LANC001",
  "leilao_id": "LEIL001",
  "usuario_id": "USER101",
  "valor": 1500.00,
  "data_hora": "2025-11-10T09:30:00",
  "status": "aceito"
}
```

**Campos:**
- `id`: Identificador único do lance
- `leilao_id`: Leilão relacionado
- `usuario_id`: Usuário que fez o lance
- `valor`: Valor do lance
- `data_hora`: Timestamp do lance
- `status`: aceito/rejeitado

---

## 🔄 Fluxo de Funcionamento

### Cenário 1: Usuário faz um lance

1. Cliente envia requisição para API Gateway
2. **processarLance** (Lambda 1):
   - Valida se o leilão existe ✓
   - Verifica se está ativo ✓
   - Confirma que lance > lance atual ✓
   - Envia para `filaLances`
3. Retorna confirmação para o usuário
4. Lance fica na fila aguardando processamento

### Cenário 2: Finalizar leilão

1. Administrador/Sistema chama **finalizarLeilao** (Lambda 2)
2. Lambda processa:
   - Busca todos os lances da fila
   - Consulta lances históricos no banco
   - Determina o maior lance
   - Atualiza status do leilão
3. Retorna resultado com vencedor e estatísticas

---

## ✅ Validações Implementadas

### processarLance

- ❌ Leilão não existe → `404 - Leilao nao encontrado`
- ❌ Leilão não está ativo → `400 - Leilao nao esta ativo`
- ❌ Lance ≤ lance atual → `400 - Lance deve ser maior que R$ X.XX`
- ❌ Parâmetros faltando → `400 - Parametros obrigatorios...`
- ✅ Lance válido → `200 - Lance recebido e enviado para processamento!`

### finalizarLeilao

- ❌ Leilão não existe → `404 - Leilao nao encontrado`
- ❌ Sem lances → `400 - Nenhum lance encontrado`
- ❌ Parâmetro faltando → `400 - Parametro obrigatorio: leilao_id`
- ✅ Leilão finalizado → `200 - Leilao finalizado com sucesso!`

---

## 🚀 Como Executar Localmente

### 1. Testar processarLance

```python
from src.processarLance import processarLance

# Fazer um lance
resultado = processarLance(
    leilao_id="LEIL001",
    usuario_id="USER101",
    valor_lance=1600.00
)

print(resultado)
```

### 2. Testar finalizarLeilao

```python
from src.finalizarLeilao import finalizarLeilao

# Finalizar leilão
resultado = finalizarLeilao(leilao_id="LEIL001")

print(resultado)
```

---

## 📈 Exemplos de Uso

### Exemplo 1: Lance válido
```
Leilão: LEIL002 (iPhone 13 Pro)
Lance atual: R$ 3200.00
Novo lance: R$ 3500.00
✅ Status: 200 - Lance aceito
```

### Exemplo 2: Lance inválido (valor baixo)
```
Leilão: LEIL002 (iPhone 13 Pro)
Lance atual: R$ 3200.00
Novo lance: R$ 3000.00
❌ Status: 400 - Lance deve ser maior que R$ 3200.00
```

### Exemplo 3: Finalizar leilão
```
Leilão: LEIL003 (Smart TV Samsung)
Lances recebidos: R$ 2000, R$ 2200, R$ 2500, R$ 2800
🏆 Vencedor: USER108
💰 Lance vencedor: R$ 2800.00
📊 Incremento: 40% sobre o valor inicial
```

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **AWS Lambda** (serverless computing)
- **AWS SQS** (fila de mensagens - em produção)
- **Python Queue** (fila local - para desenvolvimento)
- **AWS DynamoDB** (banco de dados - em produção)
- **JSON Files** (armazenamento - para desenvolvimento)
- **AWS API Gateway** (gerenciamento de APIs)

---

## 📖 Documentação Adicional

### Diagrama Visual da Arquitetura

Consulte o diagrama completo da arquitetura:

👉 **[docs/arquitetura.png](docs/arquitetura.png)** - Diagrama visual da arquitetura AWS

### Documentação Completa

Para mais detalhes sobre o projeto, consulte:

👉 **[docs/README.md](docs/README.md)** - Documentação técnica completa

---

## ✨ Vantagens da Arquitetura

### Serverless (AWS Lambda)
- 💰 Custo apenas pelo uso (pay-per-execution)
- 📈 Escalabilidade automática
- 🔧 Sem gerenciamento de servidores
- ⚡ Alta disponibilidade

### Processamento Assíncrono (Fila)
- 🔀 Desacoplamento entre componentes
- 🔄 Processamento em background
- 🛡️ Tolerância a falhas
- 📊 Controle de throughput

### Separação de Responsabilidades
- ✅ Lambda 1: Validação e recepção
- ✅ Lambda 2: Processamento e finalização
- 🧪 Fácil de testar
- 🔧 Fácil de manter e evoluir

---

## 👥 Autores

Trabalho desenvolvido para a disciplina de Sistemas Web - N2

---

## 📄 Licença

Este projeto é desenvolvido para fins acadêmicos.
