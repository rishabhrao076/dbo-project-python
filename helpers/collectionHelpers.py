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