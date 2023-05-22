#!/usr/bin/env python

from curses import wrapper, KEY_ENTER
import heapq, random

def read_cards(cardfile):
    for l in open(cardfile):
        l = l.strip()
        if l.startswith('#'):
            continue
        rank, question, answer = l.split(':')
        yield int(rank), question, answer

def save_cards(cards, cardfile):
    f = open(cardfile, 'w')
    for (rank, question, answer) in sorted(cards, reverse=True):
        print(f'{rank:d}:{question}:{answer}', file=f)
    f.close()

def select_card(cards):
    ranks = next(zip(*cards))
    if sum(ranks) == 0:
        return None
    card = random.choices(cards, weights=map(float, ranks))
    return card[0]

def replace_line(stdscr, y, x, txt, refresh=True):
    stdscr.move(y, x)
    stdscr.clrtoeol()
    stdscr.addstr(y, x, txt)
    if refresh:
        stdscr.refresh()

def main(stdscr, args):
    
    # read cards
    cards = list(read_cards(args.cardfile))
    heapq.heapify(cards)
    
    # Clear screen
    stdscr.clear()
    replace_line(stdscr, 1, 0, args.cardfile)
        
    while True:

        # select card
        card = select_card(cards)

        if card is None:
            stdscr.clear()
            replace_line(stdscr, 1, 0, args.cardfile)
            replace_line(stdscr, 3, 0, 'Congrats! No more cards left!')
            break

        rank, question, answer = card

        # ask question
        replace_line(stdscr, 3, 0, f'Q: [{rank:d}] {question}')
        replace_line(stdscr, 5, 0, 'A: press any key to reveal answer, or [qQ] to quit')

        # show answer
        k = stdscr.getkey()
        if k in 'qQ': 
            break
        replace_line(stdscr, 5, 0, f'A: {answer}')        
        replace_line(stdscr, 7, 0, '')
        replace_line(stdscr, 7, 0, f'[ENTER]=easy [SPACE]=difficult [0-5]=RESET TO N [qQ]=QUIT')
    
        # update card
        k = 'X'
        while k not in ' 012345qQ\n':
            k = stdscr.getkey()
            if k == ' ': 
                new_rank = min(5,rank+1)
            elif k == '\n':
                new_rank = max(0,rank-1)
            elif k in '012345':
                new_rank = int(k)
            else:
                new_rank = rank

        cards.remove(card)
        cards.append((new_rank, question, answer))

    # ask if update
    k = 'X'
    while k not in 'yYnN':
        replace_line(stdscr, 7, 0, f'Save results [yY/nN]?')
        k = stdscr.getkey()
        if k in 'yY': 
            save_cards(cards, args.cardfile)
            break
        elif k in 'nN':
            break

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('cardfile')
    args = parser.parse_args()

    wrapper(main, *[args])
