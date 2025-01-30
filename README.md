# FastAPI Users Demo

API de demonstração usando FastAPI Users para autenticação e gerenciamento de usuários.

## Funcionalidades

- Autenticação JWT
- Registro de usuários
- Login/Logout
- Recuperação de senha
- Verificação de email
- Gerenciamento de usuários (CRUD)
- Documentação automática (Swagger e ReDoc)

## Tecnologias

- FastAPI
- SQLAlchemy
- FastAPI Users
- SQLite
- Uvicorn

## Como Rodar

1. Clone o repositório
2. Crie um ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install "fastapi-users[sqlalchemy]" "uvicorn[standard]" aiosqlite
```

4. Rode o servidor:
```bash
python main.py
```

5. Acesse:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Rotas Disponíveis

### Autenticação
- POST /auth/register - Registro de novo usuário
- POST /auth/jwt/login - Login
- POST /auth/jwt/logout - Logout
- POST /auth/request-verify-token - Solicitar token de verificação
- POST /auth/verify - Verificar email
- POST /auth/forgot-password - Recuperar senha
- POST /auth/reset-password - Resetar senha

### Usuários
- GET /users/me - Obter usuário atual
- PATCH /users/me - Atualizar usuário atual
- GET /users/{id} - Obter usuário por ID
- PATCH /users/{id} - Atualizar usuário
- DELETE /users/{id} - Deletar usuário
