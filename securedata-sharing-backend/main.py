# main.py
from identity import generate_user_id
from encryption import generate_key, encrypt_file, decrypt_file
from hash_utils import generate_file_hash
from s3_service import S3Service
import json
import os
import time
import hashlib

# Copy Blockchain and Block classes from app.py for testing
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
        CHAIN_FILE = "blockchain.json"
        if os.path.exists(CHAIN_FILE):
            with open(CHAIN_FILE, "r") as f:
                raw_chain = json.load(f)
                for b in raw_chain:
                    timestamp = b["timestamp"]
                    if isinstance(timestamp, str):
                        try:
                            from datetime import datetime
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
        CHAIN_FILE = "blockchain.json"
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

# Import access_manager after Blockchain definition
from access_manager import can_user_access

BUCKET = "secure-blockchain-data-sharing"
REGION = "ap-south-1"

ORIGINAL = "data/uploads/sample.txt"
ENC = "data/uploads/sample.enc"
DOWN = "data/uploads/sample_downloaded.enc"
DEC = "data/uploads/sample_decrypted.txt"

print("\nCreating users...")
owner = generate_user_id("Meganathan")
auth_user = generate_user_id("bob")
bad_user = generate_user_id("eve")

key = generate_key()
encrypt_file(ORIGINAL, ENC, key)
file_hash = generate_file_hash(ORIGINAL)  # Hash original

s3 = S3Service(BUCKET, REGION)
s3.upload_file(ENC, "encrypted/sample.enc")

bc = Blockchain()
bc.add_block({
    "type": "upload",
    "file_hash": file_hash,
    "s3_bucket": BUCKET,
    "s3_key": "encrypted/sample.enc",
    "owner_id": owner,
    "authorized_users": [auth_user],
    "encrypted_key": "dummy_encrypted_key",  # For test
    "original_filename": "sample.txt"
})

print("\n--- AUTHORIZED USER TEST ---")
if can_user_access(bc, file_hash, auth_user):
    s3.download_file("encrypted/sample.enc", DOWN)
    decrypt_file(DOWN, DEC, key)
    print("ACCESS GRANTED ✅")
else:
    print("ACCESS DENIED ❌")

print("\n--- UNAUTHORIZED USER TEST ---")
if not can_user_access(bc, file_hash, bad_user):
    print("ACCESS DENIED ✅ Unauthorized blocked")