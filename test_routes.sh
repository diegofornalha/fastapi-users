#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# URL base
BASE_URL="http://localhost:8000"

# Gerar email único
TIMESTAMP=$(date +%s)
TEST_EMAIL="teste${TIMESTAMP}@exemplo.com"

echo "🔥 Iniciando testes das rotas..."
echo "Email de teste: $TEST_EMAIL"

# Função para imprimir cabeçalhos
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Função para imprimir resultados
print_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Sucesso${NC}"
    else
        echo -e "${RED}✗ Falha${NC}"
    fi
}

# 1. Registro de usuário
echo -e "\n${GREEN}1. Testando registro de usuário${NC}"
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/auth/register \
-H "Content-Type: application/json" \
-d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"senha123\"
}")
echo "Resposta: $REGISTER_RESPONSE"

# 2. Login
echo -e "\n${GREEN}2. Testando login${NC}"
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/auth/jwt/login \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=$TEST_EMAIL" \
-d "password=senha123")
echo "Resposta: $LOGIN_RESPONSE"

# Extrair token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"

# 3. Verificar usuário atual
echo -e "\n${GREEN}3. Testando rota /users/me${NC}"
ME_RESPONSE=$(curl -s -X GET $BASE_URL/users/me \
-H "Authorization: Bearer $TOKEN")
echo "Resposta: $ME_RESPONSE"

# 4. Solicitar verificação de email
echo -e "\n${GREEN}4. Testando solicitação de verificação de email${NC}"
VERIFY_REQUEST_RESPONSE=$(curl -s -X POST $BASE_URL/auth/request-verify-token \
-H "Content-Type: application/json" \
-d "{\"email\": \"$TEST_EMAIL\"}")
echo "Resposta: $VERIFY_REQUEST_RESPONSE"

# 5. Testar rota autenticada
echo -e "\n${GREEN}5. Testando rota autenticada${NC}"
AUTH_RESPONSE=$(curl -s -X GET $BASE_URL/authenticated-route \
-H "Authorization: Bearer $TOKEN")
echo "Resposta: $AUTH_RESPONSE"

# 6. Atualizar usuário
echo -e "\n${GREEN}6. Testando atualização de usuário${NC}"
UPDATE_RESPONSE=$(curl -s -X PATCH $BASE_URL/users/me \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d "{
    \"email\": \"${TEST_EMAIL}_atualizado\"
}")
echo "Resposta: $UPDATE_RESPONSE"

# 7. Solicitar redefinição de senha
echo -e "\n${GREEN}7. Testando solicitação de redefinição de senha${NC}"
FORGOT_PASSWORD_RESPONSE=$(curl -s -X POST $BASE_URL/auth/forgot-password \
-H "Content-Type: application/json" \
-d "{\"email\": \"$TEST_EMAIL\"}")
echo "Resposta: $FORGOT_PASSWORD_RESPONSE"

# 8. Logout
echo -e "\n${GREEN}8. Testando logout${NC}"
LOGOUT_RESPONSE=$(curl -s -X POST $BASE_URL/auth/jwt/logout \
-H "Authorization: Bearer $TOKEN")
echo "Resposta: $LOGOUT_RESPONSE"

echo -e "\n${GREEN}✅ Testes concluídos!${NC}" 