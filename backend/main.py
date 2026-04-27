from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import applications, dashboard, hil_review

app = FastAPI(title="Loan Underwriting AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router, prefix="/api")
app.include_router(hil_review.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
