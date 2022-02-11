"""
2021
"""
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

def permutations(n, r):
    # https://www.mathplanet.com/education/algebra-2/discrete-mathematics-and-probability/permutations-and-combinations
    # Order of r items is important
    return math.factorial(n)/math.factorial(n - r)

def combinations(n, r):
    # https://www.mathplanet.com/education/algebra-2/discrete-mathematics-and-probability/permutations-and-combinations
    # Order of r items is not important
    return math.factorial(n)/(math.factorial(n - r) * math.factorial(r))

def bernoulli_trial(n, k, p):
    # (n! / k! (n - k)!) * p^k * q^(n-k)
    # n = number of trials
    # k = number of successes
    # p = probably of success
    # q = 1 - p
    return (math.factorial(n) / (math.factorial(k) * math.factorial(n-k))) * p**k * (1-p)**(n-k)

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
    suits_found = []
    card_scores = []
    for card in hand:
        card_scores.append(score_card(card, trump_card[1]))
        if is_trump(trump_card[1], card):
            if 'trump' not in suits_found:
                suits_found.append('trump')
        else:
            if card[1] not in suits_found:
                suits_found.append(card[1])
    trump_card_score = score_card(trump_card, trump_card[1])
    if dealer:
        card_scores.append(trump_card_score)
        lowest_card = min(card_scores)
        card_scores.remove(lowest_card)
        score = sum(card_scores)
    else:
        score = sum(card_scores) - trump_card_score
    if len(suits_found) <= 2:
        score += 1
    return score

def score_hand_second_round(hand):
    max_score = 0
    for suit in suits:
        score = 0
        suits_found = []
        for card in hand:
            score += score_card(card, suit)
            if is_trump(suit, card):
                if 'trump' not in suits_found:
                    suits_found.append('trump')
            else:
                if card[1] not in suits_found:
                    suits_found.append(card[1])
        if len(suits_found) <= 2:
            score += 1
        if score > max_score:
            max_score = score

    return max_score

def is_trump(trump_suit, card):
    if card[0] == 'Jack':
        if (trump_suit == 'Hearts' or trump_suit == 'Diamonds'):
            if card[1] == 'Hearts' or card[1] == 'Diamonds':
                return True
            else:
                return False
        else:
            if card[1] == 'Clubs' or card[1] == 'Spades':
                return True
            else:
                return False
    else:
        return card[1] == trump_suit

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

    return dealer_scores_array, non_dealer_scores_array, second_round_scores_array, deck_copy, all_possible_hands.copy()

def number_of_cards_in_hand(target, hand):
    count = 0
    for card in hand:
        if target in card:
            count += 1
    return count

def number_of_bowers_in_hand(hand):
    count = 0
    for card in hand:
        if card[0] == 'Jack':
            if card[1] == 'Hearts' or card[1] == 'Diamonds':
                count += 1
    return count

def number_of_9s_and_10s(hand):
    # Return number of 9s and 10s in this hand, irrespective of trump
    count = 0
    for card in hand:
        if card[0] == '9' or card[0] == '10':
            count += 1
    return count

def card_in_hand(target_card, hand):
    for card in hand:
        if target_card == card:
            return True
    return False

def test():
    import random
    hand_size = 5
    print("Deck size: %s" % len(deck))
    print("Hand size: %s" % hand_size)
    print("Calculated combinations: %s" % int(combinations(len(deck), hand_size)))
    enumerate_hands([], deck, hand_size)
    print("Enumerated combinations: %s" % len(all_possible_hands))

    # hand = [('Jack', 'Clubs'), ('Jack', 'Spades'), ('Ace', 'Hearts'), ('10', 'Hearts'), ('9', 'Hearts')]
    # trump_card = ('9', 'Spades')
    # print("Dealer score: %s" % score_hand_first_round(hand, trump_card, dealer=True))
    # print("Non-dealer score: %s" % score_hand_first_round(hand, trump_card,dealer=False))
    # print("Second round score: %s" % score_hand_second_round(hand))

    while True:
        for i in range(20):
            random_hand_index = int(random.random() * len(all_possible_hands))
            random_hand = all_possible_hands[random_hand_index]
            print(random_hand)
            print('%s - %s' % (card_in_hand(('Ace', 'Hearts'), random_hand), random_hand))

        # remaining_deck = get_remaining_deck(deck_copy, random_hand)
        # random_trump_card_index = int(random.random() * len(remaining_deck))
        # random_trump_card = remaining_deck[random_trump_card_index]
        # print(random_trump_card)
        # print("Dealer score: %s" % score_hand_first_round(random_hand, random_trump_card,
        #                                               dealer=True))
        # print("Non-dealer score: %s" % score_hand_first_round(random_hand, random_trump_card,
        #                                                   dealer=False))
        # print("Second round score: %s" % score_hand_second_round(random_hand))
        # print("Number hearts: %s" % number_of_cards_in_hand('Hearts', random_hand))
        # print("Number bowers: %s" % number_of_bowers_in_hand(random_hand))

# test()



