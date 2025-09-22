from fastapi import FastAPI
from app.db import postgres, mongo
from app.routes import auth, teams, plays
from dotenv import load_dotenv
load_dotenv()
print("Environment variables loaded")
print("POSTGRES_URL:", postgres.DATABASE_URL)
app = FastAPI(title="Basketball Plays API")

@app.on_event("startup")
async def startup():
    
    app.state.pg = await postgres.connect_postgres()
    app.state.mongo = mongo.get_mongo_client()
    app.state.db = postgres.AsyncSessionLocal()

@app.on_event("shutdown")
async def shutdown():
    await app.state.pg.close()



# Include routes
app.include_router(auth, prefix="/auth", tags=["Auth"])
app.include_router(teams, prefix="/teams", tags=["Teams"])
app.include_router(plays, prefix="/plays", tags=["Plays"])

@app.get("/")
async def root():
    return {"message": "API running with Postgres and MongoDB!"}
