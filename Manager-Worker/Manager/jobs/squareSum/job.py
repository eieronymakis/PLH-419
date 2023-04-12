def map_function(text):
    ret = []
    for line in text:
        value=int(line.strip())
        ret.append(value ** 2)
    return ret

def reduce_function(mapped_data):
    result = sum(mapped_data)
    return result