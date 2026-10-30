from fastapi import FastAPI
from . import database, models

app = FastAPI(
    title="Restaurant Backend",
    description="API for handling restaurant orders and tracking."
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Restaurant Backend API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

from fastapi import FastAPI
from . import database, models
from .routers import orders

app = FastAPI(
    title="Restaurant Backend",
    description="API for handling restaurant orders and tracking."
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Restaurant Backend API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include routers
app.include_router(orders.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
