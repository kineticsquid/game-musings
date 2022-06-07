"""
Purpose of this script is to find three 5 letter words that cover as many of the most 
common letters appearing in non-plural 5 letter words. Optimizing first for consonants.
"""
from itertools import combinations

# http://www.scrabbleplayers.org/w/NASPA_Zyzzyva_Linux_Installation
file_name = 'NASPA_CSW21.txt'

# The most common letters have the vowells removed and are in reverse order
most_common_letters = set(['B', 'G', 'H', 'M', 'P', 'C', 'Y', 'D', 'S', 'N', 'L', 'T', 'R'])
vowells = set(['A', 'E', 'I', 'O', 'U'])

candidate_words = []
words = open(file_name, 'r')
for word in words:
    trimmed_word = word.strip().upper()
    if len(trimmed_word) == 5 and trimmed_word[4] != 'S':
        # We know this is a 5 letter word and that it is not plural (crude approach)
        letters = set(trimmed_word)
        if len(letters) == 5 and len(letters.intersection(vowells)) <= 1:
            # We know no letters are repeated and that it contains at mnost one vowell
            consonants = letters - vowells
            if len(consonants) == len(consonants.intersection(most_common_letters)):
                # Now we know that all the consonants are in the set of most common
                candidate_words.append(trimmed_word)
words.close()

print('Proceeding with %s words.'  % len(candidate_words))

count = 0
for trio in combinations(candidate_words, 3):
    count += 1
    letters = set()
    for word in trio:
        letters = letters.union(set(word))
    word_consonants = letters.intersection(most_common_letters)
    word_vowells = letters.intersection(vowells)
    if len(word_consonants) >= 13 and len(word_vowells) >= 2:
        print(trio)
        print(letters)
        print(word_consonants)
        print(word_vowells)
    if count % 10000000 == 0:
        print("Completed %sM." % int(count/1000000))