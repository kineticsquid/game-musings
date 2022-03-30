import json
import numpy as np
import os
from os.path import join
import re
import compute_scores
import json

suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']
cards = ['9', '10', 'Jack', 'Queen', 'King', 'Ace']
players = ['JK', 'KJ', 'East', 'West']

data_directory = 'data'
# data_directory = 'test'

player_regex = r"(\w+):"
upcard_regex = r"-((A|K|Q|J|10|9)(H|D|C|S))"
trump_regex = r"\+(H|D|C|S)"
card_regex = r"\s+((A|K|Q|J|10|9|\*)(H|D|C|S|\*))"

def get_pips(card_string):
    if 'A' in card_string:
        card = 'Ace'
    elif 'K' in card_string:
        card = 'King'
    elif 'Q' in card_string:
        card = 'Queen'
    elif 'J' in card_string:
        card = 'Jack'
    elif '10' in card_string:
        card = '10'
    elif '9' in card_string:
        card = '9'
    else:
        card = None
    return card

def get_suit(card_string):
    if 'H' in card_string:
        suit = 'Hearts'
    elif 'D' in card_string:
        suit = 'Diamonds'
    elif 'C' in card_string:
        suit = 'Clubs'
    elif 'S' in card_string:
        suit = 'Spades'
    else:
        suit = None
    return suit

def get_card(card_string):
    pips = get_pips(card_string)
    suit = get_suit(card_string)
    return (pips, suit)

def get_file_input(file_path):
    file = open(file_path, "r")
    contents = file.readlines()
    file.close()
    hands = []
    new_hand = {'source': file_path}
    for line in contents:
        player_results = re.findall(player_regex, line)
        if len(player_results) > 0:
            player = player_results[0]
            upcard_results = re.findall(upcard_regex, line)
            if len(upcard_results) > 0:
                upcard = get_card(upcard_results[0][0])
                new_hand['upcard'] = upcard
                new_hand['dealer'] = player
            else:
                upcard = None
            trump_results = re.findall(trump_regex, line)
            if len(trump_results) > 0:
                trump = get_suit(trump_results[0])
                new_hand['trump'] = trump
                new_hand['trump_caller'] = player
            else:
                trump = None
            card_results = re.findall(card_regex, line)
            players_cards = []
            for card_string in card_results:
                card = get_card(card_string)
                players_cards.append(card)
            new_hand[player] = players_cards
        else:
            player = None
            hands.append(new_hand)
            new_hand = {'source': file_path}
    
    # Catch the final entry if there wasn't an extra line in the file.
    if len(new_hand) > 1:
        hands.append(new_hand)

    return hands

def count_suits(hand, trump):
    suits = set([])
    for card in hand:
        if card[0] is not None:
            if card[0] != 'Jack':
                suits.add(card[1])
            else:
                if trump == 'Clubs' or trump == 'Spades':
                    if card[1] == 'Clubs' or card[1] == 'Spades':
                        suits.add(trump)
                    else:
                        suits.add(card[1])
                else:
                    if card[1] == 'Hearts' or card[1] == 'Diamonds':
                        suits.add(trump)
                    else:
                        suits.add(card[1])     
    return len(suits)          

def get_input():
    all_input = []
    for file_entry in os.listdir(data_directory):
        extension = os.path.splitext(file_entry)[1]
        if extension == '.txt':
            input = get_file_input(join(data_directory, file_entry))
            all_input = all_input + input
            file = open("%s.json" % join(data_directory, file_entry), "w")

            file.writelines(json.dumps(input,indent=4))
            file.close()

    file = open("%s.json" % join(data_directory, "all_input.json"), "w")
    file.writelines(json.dumps(all_input,indent=4))
    file.close()

    return all_input

def process_input(all_input):

    # nines_and_tens keeps a running tally of total number of 9s and 10s dealt to this player, 
    # irrespective of trump
    nines_and_tens = {}
    # farmers_hands keeps a total of number of hands this player has been dealt with at least
    # 3 nines and tens, irrespective of trump
    farmers_hands = {}
    # players_first_round_hand_scores keeps a tally of all of a players hand scores assuming 
    # trump is called in the first round on the up card
    player_first_round_hand_scores = {}
    # first_round_team_scores keeps a tally of the total scores of both teams assuming trump 
    # was called on first round
    first_round_team_scores = {'us': 0, 'them': 0}
    # players_second_round_hand_scores keeps a tally of all of a players hand scores assuming 
    # trump was called on the second round and is not the upcard
    player_second_round_hand_scores = {}
    # second_round_team_scores keeps a tally of the total scores of both teams assuming trump 
    # was called on the second round
    second_round_team_scores = {'us': 0, 'them': 0}
    # total number of hands
    total_hands = 0
    # total number of second round hands
    total_second_round_hands = 0
    # total_trump_calls is the number of times a player declares trump in either first or second
    # round
    total_trump_calls = {}
    # trump_called_hand_scores is a running total of the value of a players hand when that player
    # declares trump. If the partner of the dealer declares trump, this value includes the value of the
    # trump card the dealer picked up
    trump_called_hand_scores = {}

    for player in players:
        nines_and_tens[player] = 0
        farmers_hands[player] = 0
        player_first_round_hand_scores[player] = 0
        player_second_round_hand_scores[player] = 0
        total_trump_calls[player] = 0
        trump_called_hand_scores[player] = 0

    for hand in all_input:
        total_hands += 1
        if hand['upcard'][1] == hand['trump']:
            first_round = True
        else:
            first_round = False
            total_second_round_hands += 1

        for player in players:

            # hand_score is score of this hand for each round
            first_round_hand_score = 0
            second_round_hand_score = 0
            # nines_and_tens_count is number of 9s and 10s in this hand irrespecetive of trump
            nines_and_tens_count = 0

            for card in hand[player]:
                if card[0] == '9' or card[0] == '10':
                    nines_and_tens_count += 1

                # Score this card assuming trump was called on the first round
                first_round_hand_score += compute_scores.score_card(card, hand['upcard'][1])

                # Score this card if trump was called on the second round
                if not first_round:
                    second_round_hand_score += compute_scores.score_card(card, hand['trump'])

            # if this hand has two or fewer suits add a point to the value
            if 0 < count_suits(hand[player], hand['upcard'][1]) <= 2:
                first_round_hand_score += 1

            # if this is second round and hand has two or fewer suits add a point to the value
            if not first_round:
                if 0 < count_suits(hand[player], hand['trump']) <= 2:
                    second_round_hand_score += 1

            # Special case where one player goes alone when their partner is the dealer. Since we don't
            # know the partner's cards i.e. they're (None, None) the partner doesn't see the value of the
            # the upcard they picked up as trump, even through they don't get a change to play it. So,
            # make the value of their hand the value of the upcard. This is for the first round only.
            if hand[player][0] == (None, None):
                if first_round:
                    if hand['dealer'] == player:
                        first_round_hand_score = compute_scores.score_card(hand['upcard'], hand['upcard'][1])

            # Record scores of hands in the first round regardless of whether or not the upcard
            # was ordered up as trump
            player_first_round_hand_scores[player] = player_first_round_hand_scores[player] + first_round_hand_score
            # If trump was called on the second round, record the values of second round hands, 
            # given the trump that was called
            if not first_round:
                player_second_round_hand_scores[player] = player_second_round_hand_scores[player] + second_round_hand_score
            # Keep track of team hand score totals for each round
            if player == 'JK' or player == 'KJ':
                first_round_team_scores['us'] = first_round_team_scores['us'] + first_round_hand_score
                if not first_round:
                    second_round_team_scores['us'] = second_round_team_scores['us'] + second_round_hand_score
            else:
                first_round_team_scores['them'] =first_round_team_scores['them'] + first_round_hand_score
                if not first_round:
                    second_round_team_scores['them'] = second_round_team_scores['them'] + second_round_hand_score

            # Keep track of the number of 9s and 10s dealt to each player and the number of times a 
            # player sees a 'farmers' hand, i.e. >= 3 9s and 10s.
            nines_and_tens[player] = nines_and_tens[player] + nines_and_tens_count
            if nines_and_tens_count >= 3:
                farmers_hands[player] = farmers_hands[player] + 1

            # Keep track of how many times each player calls trump and the value of their hand. If caller's
            # partner is the dealer, add the value of the upcard to the caller's hand. If the dealer is the
            # opposition, subtract the value of the upcard from the caller's hand.
            #
            # Also keep track of borderline calls. I.e. trump calls where value is 7 or less and non-trump
            # calls where value is >= 8.
            if player == hand['trump_caller']:
                total_trump_calls[player] = total_trump_calls[player] + 1
                if not first_round:
                    trump_hand_value = second_round_hand_score
                else: 
                    trump_hand_value = first_round_hand_score
                    if hand['trump_caller'] == 'JK':
                        if hand['dealer'] == 'KJ':
                            trump_hand_value = trump_hand_value + compute_scores.score_card(hand['upcard'], hand['trump'])
                        elif hand['dealer'] != 'JK':
                            trump_hand_value = trump_hand_value - compute_scores.score_card(hand['upcard'], hand['trump'])
                    elif hand['trump_caller'] == 'KJ':
                        if hand['dealer'] == 'JK':
                            trump_hand_value = trump_hand_value + compute_scores.score_card(hand['upcard'], hand['trump'])
                        elif hand['dealer'] != 'KJ':
                            trump_hand_value = trump_hand_value - compute_scores.score_card(hand['upcard'], hand['trump'])
                    elif hand['trump_caller'] == 'East':
                        if hand['dealer'] == 'West':
                            trump_hand_value = trump_hand_value + compute_scores.score_card(hand['upcard'], hand['trump'])
                        elif hand['dealer'] != 'East':
                            trump_hand_value = trump_hand_value - compute_scores.score_card(hand['upcard'], hand['trump'])
                    elif hand['trump_caller'] == 'West': 
                        if hand['dealer'] == 'East':
                            trump_hand_value = trump_hand_value + compute_scores.score_card(hand['upcard'], hand['trump'])
                        elif hand['dealer'] != 'West': 
                            trump_hand_value = trump_hand_value - compute_scores.score_card(hand['upcard'], hand['trump'])
                trump_called_hand_scores[player] = trump_called_hand_scores[player] + trump_hand_value
            
            # Debugging print info
            # if first_round:
            #     print('1st\t%s\t%s\t%s' % (player, first_round_hand_score, hand[player]))
            # else:
            #     print('2nd\t%s\t%s\t%s' % (player, second_round_hand_score,hand[player]))

        # Debugging print info
        # print('Dealer: %s\tUpcard: %s\tTrump: %s\tCaller: %s' % (hand['dealer'], hand['upcard'], hand['trump'], hand['trump_caller']))
        # print('player_first_round_hand_scores: %s' % player_first_round_hand_scores)
        # print('player_second_round_hand_scores: %s' % player_second_round_hand_scores)
        # print('nine_and_tens: %s' % nines_and_tens)
        # print('farmers_hands: %s' % farmers_hands)
        # print('total_trump_calls %s' % total_trump_calls)
        # print('trump_called_hand_scores: %s\n' % trump_called_hand_scores)

    results = {
        'total_hands': total_hands,
        'total_second_round_hands': total_second_round_hands,
        'nines_and_tens': nines_and_tens,
        'farmers_hands': farmers_hands,
        'player_first_round_hand_scores': player_first_round_hand_scores,
        'first_round_team_scores': first_round_team_scores,
        'player_second_round_hand_scores': player_second_round_hand_scores,
        'second_round_team_scores':second_round_team_scores,
        'total_trump_calls': total_trump_calls, 
        'trump_called_hand_scores': trump_called_hand_scores
    }

    return results

def score_hand_first_round(player, hand):
    score = 0
    # First score each card
    for card in hand[player]:
        score += compute_scores.score_card(card, hand['upcard'][1])
    # if this hand has two or fewer suits add a point to the value
    if 0 < count_suits(hand[player], hand['upcard'][1]) <= 2:
        score += 1
    # Now, if this is not the dealer, adjust for the upcard. Add it if this is the partner of the dealer
    # Otherwise subtract it.
    if hand['trump_caller'] == 'JK':
        if hand['dealer'] == 'KJ':
            score = score + compute_scores.score_card(hand['upcard'], hand['trump'])
        elif hand['dealer'] != 'JK':
            score = score - compute_scores.score_card(hand['upcard'], hand['trump'])
    elif hand['trump_caller'] == 'KJ':
        if hand['dealer'] == 'JK':
            score = score + compute_scores.score_card(hand['upcard'], hand['trump'])
        elif hand['dealer'] != 'KJ':
            score = score - compute_scores.score_card(hand['upcard'], hand['trump'])
    elif hand['trump_caller'] == 'East':
        if hand['dealer'] == 'West':
            score = score + compute_scores.score_card(hand['upcard'], hand['trump'])
        elif hand['dealer'] != 'East':
            score = score - compute_scores.score_card(hand['upcard'], hand['trump'])
    elif hand['trump_caller'] == 'West': 
        if hand['dealer'] == 'East':
            score = score + compute_scores.score_card(hand['upcard'], hand['trump'])
        elif hand['dealer'] != 'West': 
            score = score - compute_scores.score_card(hand['upcard'], hand['trump'])
    return score

def score_hand_second_round(player, hand):
    score = compute_scores.score_hand_second_round(hand[player])
    return score

def trump_edge_cases(all_input):
    trump_calls_seven_or_less = {}
    trump_passes_eight_or_greater = {}

    for player in players:
        trump_calls_seven_or_less[player] = 0
        trump_passes_eight_or_greater[player] = 0

    for hand in all_input:
        total_hands += 1

    # loop through all hands and identify the edge cases 

results = get_input()
print(json.dumps(results, indent=4))

