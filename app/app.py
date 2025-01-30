from contextlib import asynccontextmanager
import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.db import User, create_db_and_tables
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, current_active_user, fastapi_users

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando criação do banco de dados e tabelas...")
    try:
        await create_db_and_tables()
        logger.info("Banco de dados e tabelas criados com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao criar banco de dados: {e}")
        raise
    yield


app = FastAPI(
    title="FastAPI Users Demo",
    description="API de demonstração do FastAPI Users com autenticação e gerenciamento de usuários",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas de autenticação
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)

# Rota de registro
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# Rota de redefinição de senha
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

# Rota de verificação
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

# Rotas de usuários
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


@app.get("/authenticated-route")
async def authenticated_route(user: Annotated[User, Depends(current_active_user)]):
    try:
        return {"message": f"Olá {user.email}!"}
    except Exception as e:
        logger.error(f"Erro na rota autenticada: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test-auth")
async def test_auth(user: Annotated[User, Depends(current_active_user)]):
    try:
        logger.debug(f"Usuário autenticado: {user.id}")
        return {"id": user.id, "email": user.email}
    except Exception as e:
        logger.error(f"Erro na autenticação: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 