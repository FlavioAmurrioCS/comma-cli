from __future__ import annotations

from typing import Any


def server() -> None:
    """Run a FastAPI server."""
    from fastapi import FastAPI
    import uvicorn

    app = FastAPI()

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"Hello": "World"}

    @app.get("/items/{item_id}")
    def read_item(item_id: int, q: str | None = None) -> dict[str, Any]:
        return {"item_id": item_id, "q": q}

    config = uvicorn.Config(
        app,
        port=5000,
        log_level="info",
    )
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    server()
