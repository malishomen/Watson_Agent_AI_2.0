#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/test")
def test():
    return {"message": "Test server works!"}

if __name__ == "__main__":
    print("Запуск тестового сервера...")
    uvicorn.run(app, host="127.0.0.1", port=8088)
