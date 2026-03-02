import hashlib
import time

def generate_user_id(username: str) -> str:
    """
    Generates a unique blockchain-style user ID
    """
    raw_data = f"{username}{time.time()}"
    return hashlib.sha256(raw_data.encode()).hexdigest()


if __name__ == "__main__":
    owner_id = generate_user_id("alice")
    user_id = generate_user_id("bob")

    print("Owner ID:", owner_id)
    print("Authorized User ID:", user_id)
