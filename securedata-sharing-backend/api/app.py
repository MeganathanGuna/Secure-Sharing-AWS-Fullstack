# app.py
from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import hashlib
import json
import os
import time
import io
import base64
import boto3
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from cryptography.fernet import Fernet

app = FastAPI(title="Secure Data Sharing with Blockchain")

CHAIN_FILE = "blockchain.json"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Master key for encrypting data keys (In production, load from secure storage)
master_key = Fernet.generate_key()

# S3 client
s3_client = boto3.client('s3')
BUCKET_NAME = "secure-blockchain-data-sharing"  # Replace with your bucket name

# Blockchain class (consolidated)
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_dict = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }
        block_string = json.dumps(block_dict, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.load_chain()

    def create_genesis_block(self):
        return Block(0, time.time(), "Genesis Block", "0")

    def load_chain(self):
        if os.path.exists(CHAIN_FILE):
            with open(CHAIN_FILE, "r") as f:
                raw_chain = json.load(f)
                for b in raw_chain:
                    # Handle timestamp as float or str
                    timestamp = b["timestamp"]
                    if isinstance(timestamp, str):
                        try:
                            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()
                        except:
                            timestamp = float(timestamp)
                    block = Block(
                        b["index"],
                        timestamp,
                        b["data"],
                        b["previous_hash"]
                    )
                    block.hash = b["hash"]
                    self.chain.append(block)
        else:
            self.chain.append(self.create_genesis_block())
            self.save_chain()

    def save_chain(self):
        with open(CHAIN_FILE, "w") as f:
            json.dump(
                [{
                    "index": b.index,
                    "timestamp": b.timestamp,
                    "data": b.data,
                    "previous_hash": b.previous_hash,
                    "hash": b.hash
                } for b in self.chain],
                f,
                indent=4
            )

    def add_block(self, data):
        last_block = self.chain[-1]
        new_block = Block(
            len(self.chain),
            time.time(),
            data,
            last_block.hash
        )
        self.chain.append(new_block)
        self.save_chain()

    def is_valid(self):
        for i in range(1, len(self.chain)):
            cur = self.chain[i]
            prev = self.chain[i - 1]

            if cur.hash != cur.calculate_hash():
                return False
            if cur.previous_hash != prev.hash:
                return False
        return True

    def get_file_info(self, file_hash):
        info = {"owner_id": None, "authorized_users": set(), "s3_key": None, "encrypted_key": None, "original_filename": None}
        for block in self.chain:
            data = block.data
            if isinstance(data, dict) and data.get("file_hash") == file_hash:
                if data.get("type") == "upload":
                    if info["owner_id"] is None:
                        info["owner_id"] = data.get("owner_id")
                        info["authorized_users"].update(data.get("authorized_users", []))
                        info["s3_key"] = data.get("s3_key")
                        info["encrypted_key"] = data.get("encrypted_key")
                        info["original_filename"] = data.get("original_filename")
                elif data.get("type") == "authorize":
                    if data.get("authorizer_id") == info["owner_id"]:
                        info["authorized_users"].add(data.get("new_user_id"))
        return info if info["owner_id"] else None

blockchain = Blockchain()

# Request Models
class AuthorizeRequest(BaseModel):
    file_hash: str
    owner_id: str
    new_user_id: str

class AccessCheckRequest(BaseModel):
    file_hash: str
    user_id: str

class DownloadRequest(BaseModel):
    file_hash: str
    user_id: str

# APIs
@app.get("/")
def root():
    return {"message": "Secure Blockchain Data Sharing API running"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    owner_id: str = Form(...)
):
    raw = await file.read()
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(raw)
    encrypted_key = Fernet(master_key).encrypt(key)
    encrypted_key_str = base64.b64encode(encrypted_key).decode()
    file_hash = hashlib.sha256(raw).hexdigest()
    s3_key = f"encrypted/{file_hash}.enc"
    s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=encrypted)
    blockchain.add_block({
        "type": "upload",
        "file_hash": file_hash,
        "owner_id": owner_id,
        "authorized_users": [],
        "s3_key": s3_key,
        "encrypted_key": encrypted_key_str,
        "original_filename": file.filename
    })
    return {
        "message": "File uploaded securely",
        "file_hash": file_hash
    }

@app.post("/authorize")
def authorize_user(req: AuthorizeRequest):
    info = blockchain.get_file_info(req.file_hash)
    if not info:
        raise HTTPException(status_code=404, detail="File not found")
    if req.owner_id != info["owner_id"]:
        raise HTTPException(status_code=403, detail="Only owner can authorize")
    blockchain.add_block({
        "type": "authorize",
        "file_hash": req.file_hash,
        "new_user_id": req.new_user_id,
        "authorizer_id": req.owner_id
    })
    return {"message": "User authorized"}

@app.post("/access-check")
def access_check(req: AccessCheckRequest):
    info = blockchain.get_file_info(req.file_hash)
    if not info:
        return {"access": False}
    allowed = (req.user_id == info["owner_id"] or req.user_id in info["authorized_users"])
    return {"access": allowed}

@app.post("/download")
def download_file(req: DownloadRequest):
    info = blockchain.get_file_info(req.file_hash)
    if not info:
        raise HTTPException(status_code=404, detail="File not found")
    if req.user_id != info["owner_id"] and req.user_id not in info["authorized_users"]:
        raise HTTPException(status_code=403, detail="Access denied")
    obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=info["s3_key"])
    encrypted = obj['Body'].read()
    encrypted_key = base64.b64decode(info["encrypted_key"])
    data_key = Fernet(master_key).decrypt(encrypted_key)
    fernet = Fernet(data_key)
    decrypted = fernet.decrypt(encrypted)
    return StreamingResponse(
        io.BytesIO(decrypted),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{info["original_filename"]}"'
        }
    )

@app.get("/chain")
def view_chain():
    return {
        "valid": blockchain.is_valid(),
        "length": len(blockchain.chain),
        "chain": [
            {
                "index": b.index,
                "timestamp": b.timestamp,
                "data": b.data,
                "hash": b.hash,
                "previous_hash": b.previous_hash
            }
            for b in blockchain.chain
        ]
    }