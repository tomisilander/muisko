#!/usr/bin/env python

from curses import wrapper, KEY_ENTER
import random


def read_cards(cardfile):
    for l in open(cardfile):
        l = l.strip()
        if l.startswith('#'):
            continue
        rank, question, answer = l.split(':')
        yield ((question, answer), int(rank)) 


def save_cards(cards, cardfile):
    f = open(cardfile, 'w')
    for ((question, answer), rank) in sorted(cards.items(), reverse=True, key=lambda qar: qar[1]):
        print(f'{rank:d}:{question}:{answer}', file=f)
    f.close()


def select(cards, selection):
    selection = selection.strip()

    if selection.startswith('_'):
        low = 0,
        high = int(selection[1:])
    elif selection.endswith('_'):
        low = int(selection[:-1]),
        high = max(rank for rank, _q, _a in cards)
    elif '_' in selection:
        low, high = map(int, selection.split('-'))
    else:
        low = high = int(selection)

    return [qa for qa,r in cards.items() if low <= r <= high]


def reset(cards, sqas, reset):
    r = reset.strip()

    if r.endswith('+'):
        dr = int(r[:-1])
    elif r.endswith('-'):
        dr = -int(r[:-1])
    else:
        dr = int(r)

    for qa in sqas:
        old_rank = cards[qa]
        new_rank = max(0,min(5,old_rank+dr))
        cards[qa] = new_rank


def choose_card(cards, sqas):
    ranks = [cards[qa] for qa in sqas]
    if sum(ranks) == 0:
        return None
    qa = random.choices(sqas, weights=map(float, ranks))[0]
    return qa


def replace_line(stdscr, y, x, txt, refresh=True):
    stdscr.move(y, x)
    stdscr.clrtoeol()
    stdscr.addstr(y, x, txt)
    if refresh:
        stdscr.refresh()


def main(stdscr, args):

    # read cards
    cards = dict(read_cards(args.cardfile))

    # select cards
    sqas = select(cards, args.select) if args.select else list(cards.keys())
    reset(cards, sqas, args.reset)


    # Clear screen
    stdscr.clear()
    replace_line(stdscr, 1, 0, args.cardfile)

    while True:

        # select card
        qa = choose_card(cards, sqas)

        if qa is None:
            stdscr.clear()
            replace_line(stdscr, 1, 0, args.cardfile)
            replace_line(stdscr, 3, 0, 'Congrats! No more cards left!')
            break

        question, answer = qa
        rank = cards[qa]

        # ask question
        replace_line(stdscr, 3, 0, f'Q: [{rank:d}] {question}')
        replace_line(
            stdscr, 5, 0, 'A: press any key to reveal answer, or [qQ] to quit')

        # show answer
        k = stdscr.getkey()
        if k in 'qQ':
            break
        replace_line(stdscr, 5, 0, f'A: {answer}')
        replace_line(stdscr, 7, 0, '')
        replace_line(
            stdscr, 7, 0, f'[ENTER]=easy [SPACE]=difficult [0-5]=RESET TO N [qQ]=QUIT')

        # update card
        k = 'X'
        while k not in ' 012345qQ\n':
            k = stdscr.getkey()
            if k == ' ':
                new_rank = min(5, rank+1)
            elif k == '\n':
                new_rank = max(0, rank-1)
            elif k in '012345':
                new_rank = int(k)
            else:
                new_rank = rank

        cards[qa] = new_rank

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
    parser.add_argument('-s', '--select', help='_h, n, l_, l_h')
    parser.add_argument('-r', '--reset', help='n-, n, n+')
    args = parser.parse_args()

    wrapper(main, *[args])
