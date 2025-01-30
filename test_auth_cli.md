# Testes de Autenticação via CLI

Este documento descreve os passos para testar manualmente as rotas de autenticação usando o CLI.

## Pré-requisitos

- FastAPI rodando em `localhost:8000`
- `curl` instalado
- Python 3.7+ com pip
- Ambiente virtual (recomendado)

## Instalação

1. Criar e ativar ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

2. Instalar dependências:
```bash
pip install "fastapi-users[sqlalchemy]" "uvicorn[standard]" aiosqlite
```

## 1. Iniciar o Servidor

```bash
# Matar qualquer instância do uvicorn rodando
pkill -f uvicorn

# Remover banco de dados de teste (opcional)
rm -f test.db

# Iniciar o servidor com logs detalhados
uvicorn app.app:app --reload --log-level debug
```

Verifique se o servidor iniciou corretamente observando as mensagens de log:
- Deve aparecer "Uvicorn running on http://127.0.0.1:8000"
- Deve mostrar "Database and tables created successfully"

## 2. Criar Novo Usuário

```bash
# Exportar variáveis para facilitar os testes
export API_URL="http://localhost:8000"
export EMAIL="test@example.com"
export PASSWORD="string123"

# Criar usuário
curl -X POST $API_URL/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}"
```

Resposta esperada:
```json
{
  "id": 1,  # O ID pode variar
  "email": "test@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

**Observações**:
- O email deve ser único
- A senha deve ter pelo menos 3 caracteres
- O usuário começa como não verificado (`is_verified: false`)

## 3. Login e Obtenção do Token

```bash
# Fazer login e salvar o token
TOKEN=$(curl -s -X POST $API_URL/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD" \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token obtido: $TOKEN"
```

Resposta esperada:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Observações**:
- O token expira em 1 hora (3600 segundos)
- Guarde o token para usar nas próximas requisições
- O formato do token é JWT (você pode decodificá-lo em jwt.io)

## 4. Testar Rota Protegida `/test-auth`

```bash
# Testar autenticação
curl -v -X GET $API_URL/test-auth \
  -H "Authorization: Bearer $TOKEN"
```

Resposta esperada:
```json
{
  "id": 1,
  "email": "test@example.com"
}
```

**Observações**:
- Esta rota retorna os dados básicos do usuário
- Útil para verificar se o token está funcionando
- O parâmetro `-v` mostra detalhes da requisição/resposta

## 5. Testar Rota Protegida `/authenticated-route`

```bash
# Testar rota com mensagem personalizada
curl -v -X GET $API_URL/authenticated-route \
  -H "Authorization: Bearer $TOKEN"
```

Resposta esperada:
```json
{
  "message": "Olá test@example.com!"
}
```

**Observações**:
- Esta rota demonstra como acessar dados do usuário em rotas protegidas
- Útil como exemplo para criar novas rotas protegidas

## 6. Gerenciamento de Usuário

```bash
# Obter informações do usuário atual
curl -X GET $API_URL/users/me \
  -H "Authorization: Bearer $TOKEN"
```

Resposta esperada:
```json
{
  "id": 1,
  "email": "test@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

**Observações**:
- Retorna dados completos do usuário autenticado
- Requer token JWT válido
- Útil para verificar status de verificação e permissões

## 7. Atualização de Dados do Usuário

```bash
# Atualizar senha do usuário
curl -X PATCH $API_URL/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "novasenha123"}'
```

Resposta esperada:
```json
{
  "id": 1,
  "email": "test@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

**Observações**:
- Permite atualizar dados do próprio usuário
- A senha deve ter pelo menos 3 caracteres
- Requer autenticação válida

## 8. Recuperação de Senha

```bash
# Solicitar token de recuperação de senha
curl -X POST $API_URL/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\"}"
```

Resposta esperada:
```json
null
```

**Observações**:
- Status 202 indica que a solicitação foi aceita
- Em produção, envia email com token de redefinição
- O token gerado é válido por tempo limitado
- Verificar logs para o token em ambiente de desenvolvimento

## 9. Verificação de Email

```bash
# Solicitar token de verificação de email
curl -X POST $API_URL/auth/request-verify-token \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\"}"
```

Resposta esperada:
```json
null
```

**Observações**:
- Status 202 indica que a solicitação foi aceita
- Em produção, envia email com link de verificação
- Verificar logs para o token em ambiente de desenvolvimento
- A verificação altera o status `is_verified` para true

## 10. Logout

```bash
# Fazer logout (invalidar token)
curl -X POST $API_URL/auth/jwt/logout \
  -H "Authorization: Bearer $TOKEN"
```

Resposta esperada:
- Status 204 No Content

**Observações**:
- Invalida o token JWT atual
- Requer token válido para logout
- Não retorna conteúdo no corpo da resposta
- Após logout, o token não pode mais ser usado

## Possíveis Erros e Soluções

1. **401 Unauthorized**
   - **Causa**: Token expirado, inválido ou ausente
   - **Solução**: 
     - Gerar novo token fazendo login novamente
     - Verificar se o header "Authorization" está correto
     - Verificar se o token não está malformado

2. **404 Not Found**
   - **Causa**: Rota não encontrada ou servidor não rodando
   - **Solução**: 
     - Verificar se o servidor está rodando em localhost:8000
     - Confirmar se a URL está correta
     - Verificar logs do servidor para erros

3. **422 Unprocessable Entity**
   - **Causa**: Dados inválidos enviados
   - **Solução**:
     - Verificar formato do JSON/dados enviados
     - Confirmar se todos os campos obrigatórios estão presentes

4. **500 Internal Server Error**
   - **Causa**: Erro no servidor
   - **Solução**: 
     - Verificar logs do servidor (terminal com uvicorn)
     - Verificar conexão com banco de dados
     - Reiniciar o servidor se necessário

## Dicas Adicionais

1. **Tokens nos Logs**:
   - Em desenvolvimento, os tokens são exibidos nos logs
   - Útil para testar redefinição de senha e verificação
   - Em produção, os tokens são enviados por email

2. **Segurança**:
   - Sempre use HTTPS em produção
   - Não compartilhe ou exponha tokens
   - Implemente rate limiting em produção
   - Configure servidor de email para notificações reais

3. **Fluxos de Usuário**:
   - Registro → Verificação → Login
   - Esqueci senha → Redefinição → Login
   - Login → Atualização de dados → Logout

4. **Ambiente de Produção**:
   - Configure servidor SMTP
   - Implemente templates de email
   - Adicione logging seguro
   - Configure rate limiting
   - Use variáveis de ambiente para secrets

## Scripts Úteis

Criar arquivo `test_auth.sh` para automatizar testes:

```bash
#!/bin/bash

# Configurações
API_URL="http://localhost:8000"
EMAIL="test@example.com"
PASSWORD="string123"

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}1. Criando usuário...${NC}"
curl -X POST $API_URL/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}"

echo -e "\n${GREEN}2. Fazendo login...${NC}"
TOKEN=$(curl -s -X POST $API_URL/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD" \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: $TOKEN"

echo -e "\n${GREEN}3. Testando rotas protegidas...${NC}"
curl -X GET $API_URL/test-auth \
  -H "Authorization: Bearer $TOKEN"

curl -X GET $API_URL/authenticated-route \
  -H "Authorization: Bearer $TOKEN"
``` 