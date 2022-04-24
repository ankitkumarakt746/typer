import curses
import random
import time
import json
import sys

lines = cols = white = black = cyan = yellow = green = red = 0

def generate_text(stdscr, length):
    content = ""
    try:
        with open("data.json", "r") as f:
            content = json.loads(f.read())
    except:
        stdscr.erase()
        msg = "Data file missing!"
        stdscr.addstr(lines//2, (cols-len(msg))//2, msg, red)
        stdscr.refresh()
        time.sleep(2)
        sys.exit()

    txt = ""
    while len(txt)<length:
        txt += content[random.randint(2, 233)] + " "

    return txt[:-1]


def display_text(window, window_height, window_width, target_text, curr_text, speed):
    window.erase()
    window.addstr(target_text)
    color = red
    if 40 < speed <= 60:
        color = yellow
    elif 60 < speed:
        color = green
    window.addstr(window_height-4, 0, f"Speed: ")
    window.addstr(window_height-4, 7, f"{speed} WPM", color)

    wrong_letters = 0
    y=0
    for i, letter in enumerate(curr_text):
        target_letter = target_text[i]
        color = green
        if letter != target_letter:
            wrong_letters += 1
            color = red
        y = i//(window_width)
        x = i-y*(window_width)
        window.addstr(y, x, letter, color)
    
    accuracy = round((len(curr_text)-wrong_letters)*100/max(len(curr_text), 1))
    color = red
    if 60 < accuracy <= 90:
        color = yellow
    elif 90 < accuracy:
        color = green
    window.addstr(window_height-4, window_width-14, f"Accuracy: ")
    window.addstr(window_height-4, window_width-4, f"{accuracy}%", color)

    window.refresh()


def start_test(stdscr, length):
    stdscr.nodelay(True)
    curses.curs_set(False)

    target_text = generate_text(stdscr, length)
    curr_text = []
    speed = 0
    start_time = time.time()

    window_width = int(2*cols/3)
    window_height = int(len(target_text)/window_width + 6)
    window = curses.newwin(window_height, window_width, (lines-window_height)//2, (cols-window_width)//2)

    msg = "Press Esc key to quit."
    stdscr.addstr(lines-2, (cols-len(msg))//2, msg)

    while True:
        mins_elapsed = max((time.time() - start_time), 1)/60  #max - to avoid zerodivisionerror in next line
        speed = int((len(curr_text)/mins_elapsed)/5)    #5 is the average word length in English

        display_text(window, window_height, window_width, target_text, curr_text, speed)

        if len("".join(curr_text)) == len(target_text):
            stdscr.nodelay(False)
            break

        try:
            key = stdscr.getkey()
        except:
            continue

        try:
            if ord(key) == 27:
                break
        except TypeError:
            continue

        if key in ("KEY_BACKSPACE", '\b', "\x7f"):
            if len(curr_text) > 0:
                curr_text.pop()
        elif len(curr_text) < len(target_text):
            curr_text.append(key)

    stdscr.addstr(lines-2, (cols-len(msg))//2, len(msg)*" ")
    stdscr.refresh()

    window.addstr(window_height-1, 0, "Press any key to continue.")
    window.refresh()
    stdscr.getch()
    window.erase()
    window.refresh()

def display_length(window, curr_text, window_width, rightSpace):
    msg = "".join(curr_text)
    window.addstr(0, window_width-rightSpace-4, 3*" ")
    window.addstr(0, window_width-rightSpace-len(msg)-1, msg)
    window.refresh()

def custom_test(stdscr):
    window_width = cols//3
    window_height = 1
    window = curses.newwin(window_height, window_width, lines//2, cols//3)

    msg = "Enter custom length: "
    window.addstr(0, 0, msg)
    msg = " characters"
    rightSpace = len(msg)
    window.addstr(0, window_width-rightSpace-1, msg)
    window.refresh()

    msg = "Press Enter key to confirm or Esc key to go back."
    spaces = len(msg)
    stdscr.addstr(lines-2, (cols-spaces)//2, msg)
    stdscr.refresh()
    
    curr_text = []
    while True:
        display_length(window, curr_text, window_width, rightSpace)
        try:
            key = stdscr.getkey()
            if ord(key) == 10:      #Pressed Enter key
                if 20 <= int("".join(curr_text)) <= 600:
                    window.erase()
                    window.refresh()
                    stdscr.addstr(lines-2, (cols-spaces)//2, spaces*" ")
                    stdscr.refresh()
                    stdscr.nodelay(False)
                    start_test(stdscr, length=int("".join(curr_text)))
                    break
                else:
                    msg = "Character length must lie between 20 and 600!"
                    stdscr.addstr((lines//2)+2, (cols-spaces)//2, msg, red)
                    stdscr.refresh()
                    time.sleep(2)
                    stdscr.addstr((lines//2)+2, (cols-spaces)//2, len(msg)*" ", red)
                    stdscr.refresh()
            elif ord(key) == 27:    #Pressed Esc key
                break
        except:
            continue
        if key in ("KEY_BACKSPACE", '\b', "\x7f"):
            if len(curr_text) > 0:
                curr_text.pop()
        elif key in ('0', '1', '2', '3', '5', '6', '7', '8', '9') and len(curr_text) < 3:
            curr_text.append(key)

        window.refresh()

    stdscr.nodelay(False)
    window.erase()
    window.refresh()
    stdscr.addstr(lines-2, (cols-spaces)//2, spaces*" ")
    stdscr.refresh()


def navigate_test_menu(stdscr, menuItems, widestItem, menuWindow):
    curr = 0
    winDisplay = lambda curr, color: menuWindow.addstr(curr, (widestItem - len(menuItems[curr]))//2, menuItems[curr], color)
    while True:
        navigate = stdscr.getch()

        if navigate == curses.KEY_UP and curr != 0:
            winDisplay(curr, white)
            curr -= 1
            winDisplay(curr, black)
        elif navigate == curses.KEY_DOWN and curr != len(menuItems)-1:
            stdscr.refresh()
            winDisplay(curr, white)
            curr += 1
            winDisplay(curr, black)
        elif navigate == curses.KEY_ENTER or navigate in [10, 13]:
            menuWindow.erase()
            menuWindow.refresh()
            if menuItems[curr] == "QUICK TEST":
                start_test(stdscr, length=40)
                display_menu(menuItems, widestItem, menuWindow, curr)
            elif menuItems[curr] == "PARAGRAPH TEST":
                start_test(stdscr, length=350)
                display_menu(menuItems, widestItem, menuWindow, curr)
            elif menuItems[curr] == "CUSTOM TEST":
                custom_test(stdscr)
                display_menu(menuItems, widestItem, menuWindow, curr)
                pass
            elif menuItems[curr] == "BACK":
                del menuWindow
                break

        menuWindow.refresh()
        stdscr.refresh()


def test_menu_screen(stdscr):
    menuItems = ["QUICK TEST", "PARAGRAPH TEST", "CUSTOM TEST", "BACK"]
    widestItem, menuWindow = create_menu_window(stdscr, menuItems)

    display_menu(menuItems, widestItem, menuWindow, currLine=0)

    navigate_test_menu(stdscr, menuItems, widestItem, menuWindow)


def display_menu(menuItems, widestItem, menuWindow, currLine):
    for line, item in enumerate(menuItems):
        color = white
        if line == currLine:
            color = black
        menuWindow.addstr(line, (widestItem - len(item))//2, item, color)
        menuWindow.addstr("\n")
        menuWindow.refresh()


def navigate_main_menu(stdscr, menuItems, widestItem, menuWindow):
    curr = 0
    winDisplay = lambda curr, color: menuWindow.addstr(curr, (widestItem - len(menuItems[curr]))//2, menuItems[curr], color)
    while True:
        navigate = stdscr.getch()

        if navigate == curses.KEY_UP and curr != 0:
            winDisplay(curr, white)
            curr -= 1
            winDisplay(curr, black)
        elif navigate == curses.KEY_DOWN and curr != len(menuItems)-1:
            winDisplay(curr, white)
            curr += 1
            winDisplay(curr, black)
        elif navigate == curses.KEY_ENTER or navigate in [10, 13]:
            menuWindow.erase()
            menuWindow.refresh()
            if menuItems[curr] == "START TEST":
                test_menu_screen(stdscr)
                display_menu(menuItems, widestItem, menuWindow, currLine=0)
            elif menuItems[curr] == "QUIT":
                break

        menuWindow.refresh()
        stdscr.refresh()


def create_menu_window(stdscr, menuItems):
    widestItem = len(max(menuItems, key=len))
    menuWindow_lines = len(menuItems)+1
    menuWindow_cols = widestItem+1
    menuWindow_y = (lines-len(menuItems))//2
    menuWindow_x = (cols-widestItem)//2

    menuWindow = curses.newwin(menuWindow_lines, menuWindow_cols, menuWindow_y, menuWindow_x)
    stdscr.refresh()

    return (widestItem, menuWindow)
        

def home_screen(stdscr):
    stdscr.erase()

    text = "Typing Speed Test"
    titleWindow = curses.newwin(1, len(text)+1, lines//6, (cols-len(text))//2)

    stdscr.refresh()

    titleWindow.addstr(text, cyan | curses.A_BOLD)
    titleWindow.refresh()

    menuItems = ["START TEST", "QUIT"]
    widestItem, menuWindow = create_menu_window(stdscr, menuItems)

    display_menu(menuItems, widestItem, menuWindow, currLine=0)

    navigate_main_menu(stdscr, menuItems, widestItem , menuWindow)


def main(stdscr):
    global lines, cols, white, black, cyan, yellow, green, red
    lines, cols = stdscr.getmaxyx()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)
    white = curses.color_pair(1)
    black = curses.color_pair(2)
    cyan = curses.color_pair(3)
    yellow = curses.color_pair(4)
    green = curses.color_pair(5)
    red = curses.color_pair(6)

    curses.curs_set(False)

    home_screen(stdscr)


curses.wrapper(main)