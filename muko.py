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
    for (rank, question, answer) in cards:
        print(f'{rank:d}:{question}:{answer}', file=f)
    f.close()

def select_card(cards):
    ranks = next(zip(*cards))
    card = random.choices(cards, weights=map(float, ranks))
    return card[0]

def replace_line(stdscr, y, x, txt):
    stdscr.move(y, x)
    stdscr.clrtoeol()
    stdscr.addstr(y, x, txt)

def main(stdscr, args):
    
    # read cards
    cards = list(read_cards(args.cardfile))
    heapq.heapify(cards)
    
    # Clear screen
    stdscr.clear()
    stdscr.addstr(1, 0, args.cardfile)
    stdscr.refresh()
        
    k = 'start'
    while k not in 'qQ':

        # select card
        card = select_card(cards)
        rank, question, answer = card

        # ask question
        replace_line(stdscr, 3, 0, f'[{rank:d}] {question}')
        replace_line(stdscr, 4, 0, '')
        stdscr.refresh()

        # show answer
        k = stdscr.getkey()
        stdscr.addstr(4, 0, answer)        
        stdscr.refresh()
    
        # update card
        k = stdscr.getkey()
        if k == ' ': 
            drank = 1
        elif k == '\n':
            drank = -1

        new_rank = max(0, min(5,int(rank)+drank))
        cards.remove(card)
        cards.append((new_rank, question, answer))
        
    save_cards(cards, args.cardfile)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('cardfile')
    args = parser.parse_args()

    wrapper(main, *[args])
