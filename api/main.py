from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.db import postgres, mongo
from app.routes import auth, teams, plays
from dotenv import load_dotenv

load_dotenv()
print("Environment variables loaded")
print("POSTGRES_URL:", postgres.DATABASE_URL)

# 👉 Create app
app = FastAPI(title="Basketball Plays API")

# 👉 CORS (NECESARIO PARA UNITY WEBGL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔴 Cambia a tu dominio en producción
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👉 Startup / Shutdown
@app.on_event("startup")
async def startup():
    app.state.pg = await postgres.connect_postgres()
    app.state.mongo = mongo.get_mongo_client()
    app.state.db = postgres.AsyncSessionLocal()

@app.on_event("shutdown")
async def shutdown():
    await app.state.pg.close()

# 👉 Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    messages = "; ".join([err["msg"] for err in errors])
    return JSONResponse(
        status_code=422,
        content={"detail": messages}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail}
    )

# 👉 Routes
app.include_router(auth, tags=["Auth"])
app.include_router(teams, tags=["Teams"])
app.include_router(plays, tags=["Plays"])

# 👉 Root
@app.get("/")
async def root():
    return {"message": "API running with Postgres and MongoDB!"}
