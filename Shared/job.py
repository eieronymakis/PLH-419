def mapper(text):
    words = text.split()
    word_counts = {}
    for word in words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1

    return [(word, count) for word, count in word_counts.items()]

def reducer(intermediate_results):
    word_counts = {}
    for word_count in intermediate_results:
        word, count = word_count
        if word in word_counts:
            word_counts[word] += count
        else:
            word_counts[word] = count

    return word_counts