# access_control.py
def is_user_authorized(blockchain, requester_id, file_hash):
    """
    Verifies whether a user is authorized to access a file
    """
    info = blockchain.get_file_info(file_hash)
    if not info:
        return False
    owner = info["owner_id"]
    authorized_users = info["authorized_users"]

    if requester_id == owner or requester_id in authorized_users:
        return True
    else:
        return False