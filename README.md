# ArUco Generator API

API FastAPI para gerar etiquetas ArUco personalizáveis e retornar as imagens em base64.

## Descrição

Esta API permite gerar etiquetas ArUco via HTTP, útil para aplicações que precisam de marcadores visuais para visão computacional.

## Endpoints

- `GET /generate`: Gera um marcador ArUco com os parâmetros passados via query string.
  - Parâmetros:
    - `id` (int, obrigatório): ID do marcador ArUco (0-49).
    - `size` (int, opcional, padrão=200): Tamanho do marcador em pixels (50-1000).
    - `margin_size` (int, opcional, padrão=10): Margem ao redor do marcador (0-100).
    - `border_bits` (int, opcional, padrão=1): Bits da borda do marcador (1-4).
  - Retorna: JSON com o ID e a imagem do marcador em base64.

- `GET /health`: Endpoint para checagem de saúde da API.

- `GET /`: Endpoint raiz com mensagem de boas-vindas.

## Como rodar localmente

1. Clone o repositório
2. Crie e ative um ambiente virtual Python
3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Rode a aplicação localmente:

```bash
uvicorn lambda:app --reload
```

5. Acesse `http://localhost:8000/docs` para ver a documentação interativa.

## Deploy na AWS Lambda

A aplicação está preparada para rodar na AWS Lambda usando o adaptador Mangum.

## Configuração do GitHub Actions para deploy automático

O repositório contém um workflow GitHub Actions que realiza o deploy automático para a função Lambda na AWS.

### Configurar secrets no GitHub

No repositório GitHub, configure os seguintes secrets:

- `AWS_ACCESS_KEY_ID`: sua chave de acesso AWS
- `AWS_SECRET_ACCESS_KEY`: sua chave secreta AWS
- `AWS_REGION`: região AWS
- `LAMBDA_FUNCTION_NAME`: nome da função Lambda

## Exemplo de uso

Requisição GET para gerar um marcador com ID 23:

```
GET /generate?id=23&size=300&margin_size=15&border_bits=1
```

Resposta:

```json
{
  "id": 23,
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

---

API desenvolvida para facilitar a geração de marcadores ArUco para aplicações de visão computacional.