# external modules
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# internal modules
from routers import router


load_dotenv()

tags_metadata = [
    {
        "name": "receipts",
        "description": "Operations related to scanning receipts.",
    },
]

app = FastAPI(openapi_tags=tags_metadata)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://shoppingify-2-0-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def docs_redirect():
    return RedirectResponse(url="/docs")


# TODO: possible usage of AWS API GATEWAY
