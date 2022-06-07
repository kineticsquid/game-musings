import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# http://www.scrabbleplayers.org/w/NASPA_Zyzzyva_Linux_Installation
file_name = 'NASPA_CSW21.txt'

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
all_words_letters = {}
all_words_count = 0
all_words_letters_count = 0
five_letter_words_letters = {}
five_letter_words_count = 0
five_letter_words_letters_count = 0
five_letter_no_plurals_letters = {}
five_letter_no_plurals_count = 0
five_letter_no_plurals_letters_count = 0
start_letters = {}
start_letters_count = 0

for letter in alphabet:
    all_words_letters[letter] = 0
    five_letter_words_letters[letter] = 0
    five_letter_no_plurals_letters[letter] = 0
    start_letters[letter] = 0

words = open(file_name, 'r')
for word in words:
    all_words_count += 1
    trimmed_word = word.strip().upper()
    for letter in trimmed_word:
        all_words_letters[letter] = all_words_letters[letter] + 1
        all_words_letters_count += 1
    if len(trimmed_word) == 5:
        five_letter_words_count += 1
        for letter in trimmed_word:
            five_letter_words_letters[letter] = five_letter_words_letters[letter] + 1
            five_letter_words_letters_count += 1
        if trimmed_word[4] != 'S':
            five_letter_no_plurals_count += 1
            for letter in trimmed_word:
                five_letter_no_plurals_letters[letter] = five_letter_no_plurals_letters[letter] + 1
                five_letter_no_plurals_letters_count += 1
            start_letters[trimmed_word[0]] = start_letters[trimmed_word[0]] + 1
            start_letters_count += 1
words.close()

all_words_letter_sorted_counts = sorted(all_words_letters.items(), key=lambda x:x[1], reverse=True)
five_letter_words_letter_sorted_counts = sorted(five_letter_words_letters.items(), key=lambda x:x[1], reverse=True)
five_letter_no_plurals_letter_sorted_counts = sorted(five_letter_no_plurals_letters.items(), key=lambda x:x[1], reverse=True)
print('All Words: %s' % all_words_count)
print(all_words_letters_count)
print(all_words_letter_sorted_counts)
print('All 5 Letter Words: %s' % five_letter_words_count)
print(five_letter_words_letters_count)
print(five_letter_words_letter_sorted_counts)
print('All Non-Plural 5 Letter Words: %s' % five_letter_no_plurals_count)
print(five_letter_no_plurals_letter_sorted_counts)
print(five_letter_no_plurals_letters_count)

