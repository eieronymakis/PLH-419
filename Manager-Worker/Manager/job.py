import json

# Define the map function
def map_function(text):
    # This function takes a file name and returns a list of tuples containing
    # word counts for each word in the file.

    # Read in the file
    # with open(file_name, 'r') as f:
    #     text = f.read()

    # Split the text into words
    words = text.split()

    # Count the number of occurrences of each word
    word_counts = {}
    for word in words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1

    # Return a list of tuples containing the word and its count
    return [(word, count) for word, count in word_counts.items()]

# Define the reduce function
def reduce_function(intermediate_results):
    # This function takes a list of tuples, where each tuple contains a word and
    # its count, and returns a dictionary containing the total count for each word.

    # Initialize an empty dictionary to store the final results
    word_counts = {}

    # Iterate over the list of intermediate results
    for word_count in intermediate_results:
        word, count = word_count

        # If the word is already in the dictionary, add the count to the existing value
        if word in word_counts:
            word_counts[word] += count
        # Otherwise, create a new entry in the dictionary for the word
        else:
            word_counts[word] = count

    result = json.dumps(word_counts, indent = 4) 
    # Return the dictionary of word counts
    return result