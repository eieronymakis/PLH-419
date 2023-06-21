def mapper(text):
    words = text.split()
    word_counts = {}
    for word in words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1

    return [(word, count) for word, count in word_counts.items()]

def reducer(merged_dict):
    reduced_dict = {}

    # Iterate over the keys and values in the merged dictionary
    for key, value in merged_dict.items():
        if isinstance(value, list):
            # Perform reduction operation on the list values
            reduced_value = sum(value)  # Example: Summing the values

            # Update the reduced dictionary with the reduced value
            reduced_dict[key] = reduced_value
        else:
            # If the value is not a list, keep it as it is in the reduced dictionary
            reduced_dict[key] = value

    return reduced_dict