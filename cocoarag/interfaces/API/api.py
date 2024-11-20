import fastapi

from cocoarag.interfaces.API import documents, users, queries


app = fastapi.FastAPI(
    title="CocoaRAGEndpoints", version="1.0", description="REST API Backend"
)

app.include_router(documents.router)
app.include_router(users.router)
app.include_router(queries.router)
