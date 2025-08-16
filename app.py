from fastapi import FastAPI, HTTPException from pydantic import BaseModel, Field import uuid, time, json, hashlib

app = FastAPI(title="MNNR API v0")
