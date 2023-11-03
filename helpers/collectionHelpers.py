import bcrypt

def group_by_index(data, index):
    grouped_data = {}
    for item in data:
        key = item[index]
        if key not in grouped_data:
            grouped_data[key] = []
        grouped_data[key].append(item)
    return grouped_data

def group_by_key(data,key):
    grouped_data = {}
    for item in data:
        item_key = item.get(key)
        if item_key not in grouped_data:
            grouped_data[item_key] = []
        grouped_data[item_key].append(item)
    return grouped_data

def generate_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')

def verify_password(hashedpassword,password):
    return bcrypt.checkpw(password.encode('utf-8'), hashedpassword.encode('utf-8'))