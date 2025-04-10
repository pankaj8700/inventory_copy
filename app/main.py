from fastapi import FastAPI
from database import create_db_and_tables
from routers import stock, inventory, indent, vc

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(stock.router)
app.include_router(inventory.router)
app.include_router(indent.router)
app.include_router(vc.router)

@app.get("/")
def main():
    return {"message": "Welcome to inventory management system"}

if __name__ == "__main__":
    import uvicorn
    import os

    # Use the PORT environment variable if available, otherwise default to 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)