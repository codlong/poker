import copy
import random
import itertools
import getopt
import sys
import matplotlib.pyplot as plt
import numpy as np
import csv

debug = False

JACK = 11
QUEEN = 12
KING = 13
ACE = 14

STRAIGHT_FLUSH = 8
FOUR_OF_A_KIND = 7
FULL_HOUSE = 6
FLUSH = 5
STRAIGHT = 4
SET = 3
TWO_PAIRS = 2
PAIR = 1
HIGH_CARD = 0

DIAMONDS = 'd'
HEARTS = 'h'
CLUBS = 'c'
SPADES = 's'
suits = [DIAMONDS, HEARTS, CLUBS, SPADES]

card_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, JACK, QUEEN, KING, ACE]

def get_deck():
    deck = []
    for card in card_values:
        for suit in suits:
            deck.append((card, suit))
    return deck

def deal(deck):
    card = random.randrange(len(deck))
    ret = deck[card]
    del deck[card]
    return ret

def format_card(card):
    value, suit = card
    if value == JACK:
        value = 'J'
    elif value == QUEEN:
        value = 'Q'
    elif value == KING:
        value = "K"
    elif value == ACE:
        value = "A"
    else:
        value = str(value)
    return "%s%s" % (value, suit)

def format_holdem_hand_for_graph(hand):
    if len(hand) > 2:
        return "INVALID"
    values = []
    
    for card in hand:
        value, suit = card
        if value == JACK:
            values.append('J')
        elif value == QUEEN:
            values.append('Q')
        elif value == KING:
            values.append('K')
        elif value == ACE:
            values.append('A')
        else:
            values.append(str(value))
    ret = ','.join(values)
    if hand[0][1] == hand[1][1]:
        ret +='s'        
    return ret

def format_hand(hand):
    out = []
    for card in hand:
        out.append(format_card(card))
    return ", ".join(out)

def format_rank(rank):
    if rank == STRAIGHT_FLUSH:
        ret = "straight flush"
    elif rank == FOUR_OF_A_KIND:
        ret = "four of a kind"
    elif rank == FULL_HOUSE:
        ret = "full house"
    elif rank == FLUSH:
        ret = "flush"
    elif rank == STRAIGHT:
        ret = "straight"
    elif rank == SET:
        ret = "set"
    elif rank == TWO_PAIRS:
        ret = "two pair"
    elif rank == PAIR:
        ret = "pair"
    else:
        ret = "high card"
    return ret

def get_suit(card):
    return card[1]

def get_value(card):
    return card[0]

def is_flush(hand):
    suit = None
    for card in hand:
        if not suit:
            suit = get_suit(card)
        else:
            if get_suit(card) != suit:
                return False
    return True

def is_straight(hand):
    values = [get_value(card) for card in hand]
    values.sort()

    #
    # Get the hard one out of the way, the wheel straight
    #
    if values == [2, 3, 4, 5, ACE]:
        return True
    else:
        unique_values = []
        for value in values:
            if value not in unique_values:
                unique_values.append(value)
        #
        # Check to see if the cards are all unique
        #
        if len(values) != len(unique_values):
            return False
        #
        # Check to see if they are consecutive
        #
        return max(values) - min(values) == 4    

def is_straight_flush(hand):
    return is_straight(hand) and is_flush(hand)

def is_four_of_a_kind(hand):
    return has_num_cards(hand, 4)

def is_full_house(hand):
    return has_pair(hand) and has_set(hand)

def has_num_cards(hand, num):
    values = [get_value(card) for card in hand]
    for value in values:
        if card_count(values, value) == num:
            return True
    return False   

def has_num_cards_ranking(hand, num):
    values = [get_value(card) for card in hand]
    ret = 0
    for value in values:
        num_matches = card_count(values, value)
        if num_matches == num and value > ret:
            ret = value
    return ret  

def has_set(hand):
    return has_num_cards(hand, 3)    

def has_pair(hand):
    return has_num_cards(hand, 2)

def has_pair_of(hand, value):
    if [get_value(card) for card in hand].count(value) == 2:
        return True
    return False   

def has_two_pair(hand):
    ret = False
    pair = has_num_cards_ranking(hand, 2)
    if pair > 0:
        rest = [card for card in hand if get_value(card) != pair]
        ret = has_num_cards(rest, 2)
    return ret

def high_card(hand):
    values = [get_value(card) for card in hand]
    values.sort()
    ret = values[4]
    #
    # The high card is always the card with the greatest value EXCEPT
    # for a wheel straight
    #
    if ret == ACE and is_straight(hand):
        if 5 in values:
            ret = 5
    return ret

def card_count(values, value):
    count = 0
    for v in values:
        if v == value:
            count += 1
    return count

def hand_rank(hand):
    if is_straight_flush(hand):
        rank = STRAIGHT_FLUSH
    elif is_four_of_a_kind(hand):
        rank = FOUR_OF_A_KIND
    elif is_full_house(hand):
        rank = FULL_HOUSE
    elif is_flush(hand):
        rank = FLUSH
    elif is_straight(hand):
        rank = STRAIGHT
    elif has_set(hand):
        rank = SET
    elif has_two_pair(hand):
        rank = TWO_PAIRS
    elif has_pair(hand):
        rank = PAIR
    else:
        rank = HIGH_CARD
    return rank

def straight_rank(hand):
    values = [get_value(card) for card in hand]
    values.sort()

    if values == [2, 3, 4, 5, ACE]:
        ret = 5
    else:
        ret = max(values)
    return ret

def get_kickers(hand):
    kickers = []
    set_value = has_num_cards_ranking(hand, 3)
    if set_value:
        for card in hand:
            value = get_value(card)
            if value != set_value:
                kickers.append(value)
    else:
        pair_value = has_num_cards_ranking(hand, 2)
        if pair_value:
            for card in hand:
                value = get_value(card)
                if value != pair_value:
                    kickers.append(value)
        else:
            kickers = [get_value(card) for card in hand]
    return sorted(kickers, reverse=True)

def get_winners(hands):
    hand_rankings = sorted([(hand_rank(hand), hand) for hand in hands], reverse = True)
    max_ranking = hand_rankings[0][0]
    winners = []

    for rank, hand in hand_rankings:
        if rank == max_ranking:
            winners.append(hand)
        else:
            break

    if len(winners) > 1:
        if max_ranking == STRAIGHT_FLUSH:           
            high_straight = max([straight_rank(hand) for hand in winners])
            for hand in winners:
                if high_straight not in [get_value(card) for card in hand]:
                    winners.remove(hand)
        elif max_ranking == FOUR_OF_A_KIND:
            high_four = max([has_num_cards_ranking(hand, 4) for hand in winners])
            for hand in winners:
                if high_four not in [get_value(card) for card in hand]:
                    winners.remove(hand)
        elif max_ranking == FULL_HOUSE:
            high_three = max([has_num_cards_ranking(hand, 3) for hand in winners])
            for hand in winners:
                if high_three not in [get_value(card) for card in hand]:
                    winners.remove(hand)
        elif max_ranking == FLUSH:
            kickers = [(hand, get_kickers(hand)) for hand in winners]
            max_kicker = max([kicker[1] for kicker in kickers])
            winners = [hand[0] for hand in kickers if hand[1] == max_kicker]
        elif max_ranking == STRAIGHT:       
            high_straight = max([straight_rank(hand) for hand in winners])
            for hand in winners:
                if high_straight not in [get_value(card) for card in hand]:
                    winners.remove(hand)
        elif max_ranking == SET:
            high_set = max([has_num_cards_ranking(hand, 3) for hand in winners])
            for hand in winners:
                if high_set not in [get_value(card) for card in hand]:
                    winners.remove(hand)
            if len(winners) > 1: 
                # Down to kickers
                kickers = [(hand, get_kickers(hand)) for hand in winners]
                max_kicker = max([kicker[1] for kicker in kickers])
                winners = [hand[0] for hand in kickers if hand[1] == max_kicker]
        elif max_ranking == TWO_PAIRS:
            pairs = sorted([has_num_cards_ranking(hand, 2) for hand in winners], reverse = True)
            high_pair = pairs[0]
          
            winners = [hand for hand in winners if has_num_cards_ranking(hand, 2) == high_pair]
            if len(winners) > 1:
                # We might have the same top pair but different bottom pairs
                candidates = [[card for card in hand if get_value(card) != high_pair] for hand in winners]
                second_pair = sorted([has_num_cards_ranking(hand, 2) for hand in candidates], reverse = True)
                second_pair_value = second_pair[0]
                winners = [hand for hand in winners if has_pair_of(hand, second_pair_value)] 
                if len(winners) > 1: 
                    # We have the same two pair!
                    kickers = [(hand, sorted([k for k in [v[0] for v in hand] if k != high_pair and k != second_pair_value])) for hand in winners]
                    max_kicker = max([kicker[1] for kicker in kickers])
                    winners = [hand[0] for hand in kickers if hand[1] == max_kicker]
        elif max_ranking == PAIR:
            pairs = [has_num_cards_ranking(hand, 2) for hand in winners]
            high_pair = max(pairs)
            winners = [hand for hand in winners if has_num_cards_ranking(hand, 2) == high_pair]
            if len(winners) > 1: 
                # Down to kickers
                kickers = [(hand, get_kickers(hand)) for hand in winners]
                max_kicker = max([kicker[1] for kicker in kickers])
                winners = [hand[0] for hand in kickers if hand[1] == max_kicker]
        elif max_ranking == HIGH_CARD:                        
            kickers = [(hand, get_kickers(hand)) for hand in winners]
            max_kicker = max([kicker[1] for kicker in kickers])
            winners = [hand[0] for hand in kickers if hand[1] == max_kicker]
    return winners

def get_best_holdem_hand(hole, field):
    possible_hands = itertools.combinations(hole + field, 5)
    return get_winners(possible_hands)[0]

def run_hold_em_hand(num_hands, against = None, flop_only = False):
    deck = get_deck()
    if against is not None:
        for card in against:
            deck.remove(card)
    hands = [[deal(deck) for i in range(2)] for j in range(num_hands)]
    if against is not None:
        hands.append(against)
    field = [deal(deck) for i in range(5 if not flop_only else 3)]

    best_hands = []
    for hole in hands:
        best_hand = get_best_holdem_hand(hole, field)
        best_hands.append((hole, best_hand))

    winners = get_winners([hand[1] for hand in best_hands])
    hole_winners = [c[0] for c in best_hands if c[1] in winners]

    if debug:
        print("field: %s" % format_hand(field))
        print("winning hands:")
        for winner in hole_winners:
            print("\t%s" % format_hand(winner))
        print("%s: %s" % (format_hand(sorted(winners[0])), format_rank(hand_rank(winners[0]))))
    return hole_winners, winners

def run_five_card_sim(num_runs, num_hands):   
    winning_rank = [0] * 9
    for i in range(num_runs):    
        deck = get_deck()
        num_cards = 5
        hands = [[deal(deck) for i in range(num_cards)] for j in range(num_hands)] 

        if verbose:
            for hand in hands:
                print(format_hand(hand))

        winners = get_winners(hands)
        winning_rank[hand_rank(winners[0])] += 1

        if verbose:
            print("Winners with %s" % format_rank(hand_rank(winners[0])))
            for winner in winners:
                print("\t%s" % format_hand(winner))

    for i in range(len(winning_rank)):
        print("%s: %d" % (format_rank(i), winning_rank[i]))

def run_hold_em_hand_sim(num_hands, num_players, test_hand, flop_only = False):
    wins = 0
    winning_rank = [0] * 9 # number of ranks to keep track of
    for i in range(num_hands): 
        if verbose and i % 100 == 0:
            print("Running hand %d" % i)
        hole_winners, winners = run_hold_em_hand(num_players - 1, test_hand, flop_only)
        
        if test_hand in hole_winners:
            wins += 1
            winning_rank[hand_rank(winners[0])] += 1

    if debug:
        print("%s won %.1f%%" % (format_hand(test_hand), float(wins)/float(num_hands) * 100.0))
        for i in range(len(winning_rank)):
                print("%s: %d" % (format_rank(i), winning_rank[i]))
    return wins
            
def run_hold_em_sim(num_hands, num_players, flop_only):
    #
    # Stick with two suits. This will give us suited and non-suited with fewer starting possibilities
    #
    suits = [DIAMONDS, HEARTS]

    deck = []
    for card in card_values:
        for suit in suits:
            deck.append((card, suit))

    potential_hands = list(itertools.combinations(deck, 2))
    test_hands = []

    #
    # Add all pairs, all off-suit hands, and all diamond hands. This gets us to the 169 possible
    # Hold 'em hands
    #
    for hand in potential_hands:
        if hand[0][0] == hand[1][0]:
            test_hands.append(hand) 
        elif hand[0][1] == DIAMONDS and hand[1][1] == HEARTS:
            test_hands.append(hand)
        elif hand[0][1] == DIAMONDS and hand[1][1] == DIAMONDS:
            test_hands.append(hand)

    hands = []
    for test_hand in test_hands:
        test_hand = list(test_hand)
        if verbose:
            print("testing %s" % format_hand(test_hand))
        wins = run_hold_em_hand_sim(num_hands, num_players, test_hand, flop_only)
        if verbose:
            print("%s won %.2f%%" % (format_hand(test_hand), (float(wins)/float(num_hands)) * 100.0))
        hands.append([float(wins)/float(num_hands),test_hand])
    hands = sorted(hands, reverse=True)    
    
    return(hands)

def test_winners():
    hands =[
        [(2, 'h'), (2, 'd'), (4, 'h'), (4, 'd'), (KING, 'h')],
        [(2, 'd'), (2, 'h'), (4, 'd'), (4, 'h'), (ACE, 'd')]
    ]
    print(get_winners(hands))

def split_results(results, threshold):
    rest = results
    # 
    # Results are a list of [result percentage, hand], where hand is a list
    # [card 1, card 2]. Each card is a tuple, (value, suit).
    # 
    pairs = []    
    suited_consecutive = []
    suited_connectors = []

    #
    # ALL pairs
    #
    pairs = [
        result for result in results 
        if result[1][0][0] == result[1][1][0]
    ]
    rest = [result for result in results if result not in pairs]
    #
    # ALL suited consecutive
    #
    suited_consecutive = [
        result for result in rest 
        if result[1][0][1] == result[1][1][1]
        and (result[1][1][0] - result[1][0][0] == 1 or (result[1][1][0] == ACE and result[1][0][0] == 2))
    ]
    rest = [result for result in rest if result[0] > threshold and result not in suited_consecutive]
    #
    # Suited connectors over threshold
    #
    suited_connectors = [
        result for result in rest 
        if result[1][0][1] == result[1][1][1]
        and (result[1][1][0] - result[1][0][0] < 5 or (result[1][1][0] == ACE and result[1][0][0] in [5, 4, 3]))
    ]
    #
    # 'Field' hands over threshold
    #
    rest = [result for result in rest if result[0] > threshold and result not in suited_connectors]
    
    ret = [
        ("Pairs", pairs), 
        ("Suited Consecutive", suited_consecutive),
        ("Suited Connectors", suited_connectors),
        ("Field", rest)
    ]

    return ret

def graph(hand_results, threshold, top_10_ev, top_20_ev):
    num_rows = len(hand_results)
    fig, subplots = plt.subplots(num_rows, 1)
    fig.suptitle('Hold ''em Hand Results -- EV > %.1f%%' % (threshold * 100.0))

    top_10_ev *= 100.0
    top_20_ev *= 100.0

    i = 1
    for title, hr in hand_results:        
        hand_types = [format_holdem_hand_for_graph(hand[1]) for hand in hr]
        values = [hand[0] * 100.0 for hand in hr]

        plt.subplot(num_rows, 1, i)
        plt.axes
        plt.ylabel(title)
        x = np.arange(len(hand_types))
        y = np.array(values)
    
        mask1 = y >= top_10_ev
        mask2 = np.logical_and(y < top_10_ev, y >= top_20_ev)
        mask3 = np.logical_and(y < top_20_ev, y >= threshold)
        mask4 = y < threshold * 100.0

        # Create bars
        bar = plt.bar(x[mask1], y[mask1], color = 'green')
        plt.bar_label(bar, fmt='%.1f%%')
        bar = plt.bar(x[mask2], y[mask2], color = 'purple')
        plt.bar_label(bar, fmt='%.1f%%')
        bar = plt.bar(x[mask3], y[mask3], color = 'red')
        plt.bar_label(bar, fmt='%.1f%%')
        bar = plt.bar(x[mask4], y[mask4], color = 'grey')
        plt.bar_label(bar, fmt='%.1f%%')

        # Create names on the x-axis
        plt.xticks(x, hand_types)

        i += 1

    subplots[len(subplots) - 1].set_xlabel('hand')

    # Show graphic
    plt.show()

def read_csv(fname):
    hand_results = []
    with open(fname, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            hand_ev = float(row[1])                    
            hand_value = row[0]
            
            suited = 's' in hand_value
            if suited:
                hand_value = hand_value.replace('s', '')

            card_values = hand_value.split(',')
            new_values = []
            for card_value in card_values:
                if card_value == 'J':
                    card_value = JACK
                elif card_value == 'Q':
                    card_value = QUEEN
                elif card_value == 'K':
                    card_value = KING
                elif card_value == 'A':
                    card_value = ACE
                else:
                    card_value = int(card_value)
                new_values.append(card_value)
            
            v = [hand_ev, [(new_values[0], DIAMONDS), (new_values[1], DIAMONDS if suited else HEARTS)]]
            hand_results.append(v)   
    return hand_results             

def usage():
    msg = """
%s [options]
Parameters
----------
--hands=[hands] the number of player hands in each run (for holdem)
--runs=[runs] the number of hands (runs) to play. For holdem, it will run 
       runs * 169, one for each hand possibility
--game=[game] Which game (holdem, five) to play. Defaults to holdem
--flop For a flop game, only run through the flop, ignoring turn and river.
       Defaults to false.
    """ % sys.argv[0]
    print(msg)

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "g:h:r:fvl:", ["hands=", "runs=", "game=", "flop"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        usage()
        exit(1)

    runs = None
    hands = None
    game = "holdem"
    flop_only = False
    verbose = False
    load_file = None
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--hands"):
            hands = int(a)
        elif o in ("-r", "--runs"):
            runs = int(a)
        elif o in ("-g", "--game"):
            game = a
        elif o in ("-f", "--flop"):
            flop_only = True
        elif o in ("-l"):
            load_file = a
            verbose = True
        else:
            usage()
            assert False, "unhandled option"
    if not load_file and (not hands or not runs):
        usage()
        exit(0)

    if  game not in ('holdem', 'five'):
        print("Unknown game %s" % game)
        usage()
        exit(1)

    if game == 'holdem':
        if not load_file:
            hand_results = run_hold_em_sim(runs, hands, flop_only)
            fname = "%s_%d_runs_%d_hands%s.csv" % (game, runs, hands, "_floponly" if flop_only else "")
            with open(fname, 'w') as f:
                for hand in hand_results:
                    f.write("\"%s\", %f\n" % (format_holdem_hand_for_graph(hand[1]), hand[0]))
            print("wrote %s" % fname)
        else:
            hand_results = read_csv(load_file) 

        if verbose:
            #
            # Show graph. Threshold will be top 25% of hands. There are 169 possible hands.
            #
            print(len(hand_results))
            threshold = hand_results[round(169 * .25)][0]

            # Determine EV of top 10% and top 20% hands
            top_10_ev = hand_results[round(169 * .1)][0]
            top_20_ev = hand_results[round(169 * .2)][0]

            graph(split_results(hand_results, threshold), threshold, top_10_ev, top_20_ev)
    else:
        run_five_card_sim(runs, hands)
