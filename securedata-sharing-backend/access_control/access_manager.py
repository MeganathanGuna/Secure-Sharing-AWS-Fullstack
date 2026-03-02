# access_manager.py
import json  # If needed for any reason

def can_user_access(blockchain, file_hash, user_id):
    info = blockchain.get_file_info(file_hash)
    if not info:
        return False
    if user_id == info['owner_id'] or user_id in info['authorized_users']:
        return True
    return False