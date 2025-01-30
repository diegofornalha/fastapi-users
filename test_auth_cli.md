# Testes de Autenticação via CLI

Este documento descreve os passos para testar manualmente as rotas de autenticação usando o CLI.

## Pré-requisitos

- FastAPI rodando em `localhost:8000`
- `curl` instalado

## 1. Iniciar o Servidor

```bash
# Matar qualquer instância do uvicorn rodando
pkill -f uvicorn

# Remover banco de dados de teste (opcional)
rm -f test.db

# Iniciar o servidor com logs detalhados
uvicorn app.app:app --reload --log-level debug
```

## 2. Criar Novo Usuário

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"string123"}'
```

Resposta esperada:
```json
{
  "id": 12,
  "email": "test@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

## 3. Login e Obtenção do Token

```bash
curl -X POST http://localhost:8000/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=string123"
```

Resposta esperada:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 4. Testar Rota Protegida `/test-auth`

```bash
curl -v -X GET http://localhost:8000/test-auth \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

Resposta esperada:
```json
{
  "id": 12,
  "email": "test@example.com"
}
```

## 5. Testar Rota Protegida `/authenticated-route`

```bash
curl -v -X GET http://localhost:8000/authenticated-route \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

Resposta esperada:
```json
{
  "message": "Olá test@example.com!"
}
```

## Possíveis Erros

1. **401 Unauthorized**
   - Token expirado ou inválido
   - Solução: Gerar um novo token fazendo login novamente

2. **404 Not Found**
   - Rota não encontrada
   - Solução: Verificar se o servidor está rodando e se a URL está correta

3. **500 Internal Server Error**
   - Erro no servidor
   - Solução: Verificar os logs do servidor para mais detalhes

## Dicas

1. Para ver os logs detalhados do servidor, mantenha o terminal com o uvicorn aberto
2. Use o parâmetro `-v` no curl para ver os detalhes da requisição/resposta
3. O token JWT expira em 1 hora (3600 segundos)
4. Para testar com um novo usuário, delete o arquivo `test.db` e reinicie o servidor 