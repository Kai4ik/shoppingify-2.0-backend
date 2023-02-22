from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from routers import router

from dotenv import load_dotenv
load_dotenv()

tags_metadata = [
    {
        "name": "receipts",
        "description": "Operations related to scanning receipts. ",
    },
]

app = FastAPI(openapi_tags=tags_metadata)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def docs_redirect():
    return RedirectResponse(url="/docs")
