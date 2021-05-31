import math
import numpy as np
import time
suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']
cards = ['9', '10', 'Jack', 'Queen', 'King', 'Ace']

deck = []
for suit in suits:
    for card in cards:
        deck.append((card, suit))

deck_copy = deck.copy()

all_possible_hands = []

def enumerate_hands(current_hand, current_deck, hand_size):
    # print("Current Hand: %s" % current_hand)
    # print("Current Deck: %s" % current_deck)
    # print("All Hands: %s" % all_possible_hands)
    if len(current_hand) == hand_size:
        all_possible_hands.append(current_hand)
    else:
        while len(current_deck) > 0:
            current_card = current_deck[0]
            current_deck.remove(current_deck[0])
            new_deck = current_deck.copy()
            new_hand = current_hand.copy()
            new_hand.append(current_card)
            enumerate_hands(new_hand, new_deck, hand_size)

def combinations(n, r):
    # https://www.mathplanet.com/education/algebra-2/discrete-mathematics-and-probability/permutations-and-combinations
    return math.factorial(n)/(math.factorial(n - r) * math.factorial(r))

def score_card(card, trump_suit):
    score = 0
    if card[1] == trump_suit:
        if card[0] == 'Jack':
            score = 4
        elif card[0] == 'Ace':
            score = 3
        elif card[0] == 'King':
            score = 2
        elif card[0] == 'Queen':
            score = 2
        else:
            score = 1
    elif card[0] == 'Jack':
        if trump_suit == 'Hearts' or trump_suit == 'Diamonds':
            if card[1] == 'Hearts' or card[1] == 'Diamonds':
                score = 3
        elif trump_suit == 'Clubs' or trump_suit == 'Spades':
            if card[1] == 'Clubs' or card[1] == 'Spades':
                score = 3
    elif card[0] == 'Ace':
        score = 2
    else:
        score = 0
    return score

def score_hand_first_round(hand, trump_card, dealer):
    score = 0
    suits_found = []
    for card in hand:
        score += score_card(card, trump_card[1])
        if card[1] not in suits_found:
            suits_found.append(card[1])
    if len(suits_found) <= 2:
        score += 1
    if trump_card is not None:
        trump_card_score = score_card(trump_card, trump_card[1])
        if dealer:
            score += trump_card_score
        else:
            score -= trump_card_score
    return score

def score_hand_second_round(hand):
    max_score = 0
    for suit in suits:
        score = 0
        for card in hand:
            score += score_card(card, suit)
        if score > max_score:
            max_score = score

    suits_found = []
    for card in hand:
        if card[1] not in suits_found:
            suits_found.append(card[1])
    if len(suits_found) <= 2:
        max_score += 1

    return max_score

def get_remaining_deck(deck, hand):
    new_deck = deck.copy()
    for card in hand:
        new_deck.remove(card)
    return new_deck

def calculate_all_possible_scores():

    hand_size = 5
    print("Deck size: %s" % len(deck))
    print("Hand size: %s" % hand_size)
    print("Calculated combinations: %s" % int(combinations(len(deck), hand_size)))
    enumerate_hands([], deck, hand_size)
    print("Enumerated combinations: %s" % len(all_possible_hands))
    # print(all_possible_hands)

    # num_possible_scores = len(all_possible_hands) * (len(deck_copy) - hand_size)
    # dealer_scores = np.zeros(num_possible_scores, dtype=int)
    # non_dealer_scores = np.zeros(num_possible_scores, dtype=int)
    # second_round_scores = np.zeros(num_possible_scores, dtype=int)

    dealer_scores = []
    non_dealer_scores = []
    second_round_scores = []

    count = 0
    start_time = time.time()
    for hand in all_possible_hands:
        remaining_deck = get_remaining_deck(deck_copy, hand)
        for trump_card in remaining_deck:
            dealer_scores.append(score_hand_first_round(hand, trump_card, dealer=True))
            non_dealer_scores.append(score_hand_first_round(hand, trump_card, dealer=False))
            second_round_scores.append(score_hand_second_round(hand))

            count += 1
            if count % 100000 == 0:
                print("%s combinations processed - %.1f sec" % (count, time.time() - start_time))

    print("%s combinations processed - %.1f sec" % (count, time.time() - start_time))
    dealer_scores_array = np.array(dealer_scores)
    non_dealer_scores_array = np.array(non_dealer_scores)
    second_round_scores_array = np.array(second_round_scores)

    return dealer_scores_array, non_dealer_scores_array, second_round_scores_array



