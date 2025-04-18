import curses
# curses installed on Liunx, manually install on windows as following:
# pip install windows-curses

from node import Naver
import datetime
from enum import Enum


# All stat can Jump to itself (Start a new command)
# All stat can quit() to force exit (@TODO autosave needed)
JUMP_TAB={
    "RECORD":["ADD","INSERT","DELETE"],
        "ADD":["ADD","INSERT","DELETE"],
        "INSERT":["INSERT","ADD","DELETE"],
        "DELETE":["DELETE","ADD","INSERT"],

    "NAV":["MVTO","RECORD","IDLE"],
        "MVTO":["MVTO","NAV","IDLE"],
    "IDLE":["RECORD","NAV"],
}

CMD_TIPS={
    "RECORD":"listname:string",
    "ADD":"comment:string(optional)",
    "INSERT":"former_point:int | comment:string(optional)",
    "DELETE":"at_point:int",
    "NAV":"direction:int listname:string",
    "MVTO":"at_point:int", # @ayx ADD optional speed control here
    "IDLE":"",
}


class GT_STATUS(Enum):
    RECORD = "0"
    MOV = "1"
    NAV = "1-1"
    CMD = "1-2"
    IDLE = "2"
def auto_stat_doc():
    """
    deprecated, Only for  Hierarchical FSM
    """
    names = [i.name for i in GT_STATUS]
    res={i.name:[] for i in names}
    p,q = 0,1
    for i in range(len(GT_STATUS)-1):
        e1, e2 = GT_STATUS[names[p]], GT_STATUS[names[q]]
        if len(e1.value) == len(e2.value):
            pass
    
    # for name, label in [i for i in GT_STATUS]:


MAX_CMD_ROWS = 15

def get_logo(height, width):

    __logo = r"""  ___       ______      _           _     _____ _____       _____ _____      _____ _____ 
 / _ \      | ___ \    | |         | |   |_   _|_   _|     |  __ |_   _|    |  _  / __  \
/ /_\ \ __ _| |_/ /___ | |__   ___ | |_    | |   | |       | |  \/ | |______| |/' `' / /'
|  _  |/ _` |    // _ \| '_ \ / _ \| __|   | |   | |       | | __  | |______|  /| | / /  
| | | | (_| | |\ | (_) | |_) | (_) | |_   _| |_ _| |_      | |_\ \ | |      \ |_/ ./ /___
\_| |_/\__, \_| \_\___/|_.__/ \___/ \__|  \___/ \___/       \____/ \_/       \___/\_____/
        __/ |                                                                            
       |___/                                                                             """

    __logo_small = r"""    _        ___     _        _     ___ ___        ___ _____     __ ___ 
   /_\  __ _| _ \___| |__ ___| |_  |_ _|_ _|      / __|_   ____ /  |_  )
  / _ \/ _` |   / _ | '_ / _ |  _|  | | | |      | (_ | | ||___| () / / 
 /_/ \_\__, |_|_\___|_.__\___/\__| |___|___|      \___| |_|     \__/___|
       |___/                                                            """

    __logo_text = "AgRobot II  GT-02"
    
    for logo in [__logo, __logo_small, __logo_text]:
        w = max([len(i.strip()) for i in logo.split("\n")])
        h = len(logo.split("\n"))
        # print(f"Logo width {w} height {h}\nScreen width {width} half height {height//2}")
        if width < w or height//2 < h:
            continue
        else:
            return logo


def setup(win):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)
    # curses.nocbreak()
    
    win.keypad(False)
    curses.echo()
    
    curses.curs_set(1)
    

def frame_welcome(win,height, width):
    win.nodelay(False)
    __wel_text = "DSLab AgRobot Terminal for GT-02"
    __wel_text2 = "<Press Any to Continue, 'q' to quit>"
    k = None
    
    win.clear()
    win.refresh()
    
    start_y = int((height // 2))
    start_x_wel_text= int((width // 2) - (len(__wel_text) // 2) - len(__wel_text) % 2)
    start_x_wel_text2= int((width // 2) - (len(__wel_text2) // 2) - len(__wel_text2) % 2)

    logo=get_logo(height, width)

    win.attron(curses.color_pair(1))
    for i,_l in enumerate(logo.split("\n")[::-1]):
        start_x_l= int((width // 2) - (len(_l) // 2) - len(_l) % 2)
        win.addstr(start_y - i - 1, start_x_l,_l)
        
    win.attroff(curses.color_pair(1))
    
    
    win.attron(curses.color_pair(2))
    win.attron(curses.A_BOLD)

    # Rendering title
    win.addstr(start_y + 1, start_x_wel_text, __wel_text)

    # Turning off attributes for title
    win.attroff(curses.color_pair(2))
    win.attroff(curses.A_BOLD)
    
    win.addstr(start_y + 3, start_x_wel_text2, __wel_text2)
    
    win.refresh()
    k = win.getch()
    if k == ord("q"):
        exit()
    win.clear()
    win.refresh()
    win.nodelay(True)



def main_loop(win,height, width):
    
    
    input_head = ' admin@GT-02 > '
    info_head = '│ Tips: '
    
    max_cmd_rows = MAX_CMD_ROWS if MAX_CMD_ROWS < height-3 else height -3
    
    y_split = height - 3
    y_info = height - 2
    y_input = height - 1
    cmds = ["History Logs"]
    
    exit_flag = False
    
    cur_stat = "IDLE"
    
    raw_input = ""
    
    warn = None
    

    puber = None
    
    while not exit_flag:
        
        height, width = win.getmaxyx()
        
        info_body = f"Current {cur_stat}, Leagal Command: {"".join(["<%s:%s>  "%(i,CMD_TIPS[i]) for i in JUMP_TAB[cur_stat]])} " 
    
        # @ayx pathlist add info
        if puber: 
            cmds = puber.log[-max_cmd_rows:]
            # print("puber has been set")
        for i,cmd in enumerate(cmds):
            win.addstr(i, 0, cmd)
            # win.addstr(i+1, 0, str(datetime.datetime.now()))
            
    
        win.addstr(y_split, 0, "┌" + '─'*(width-2))
        if not warn:
            win.addstr(y_info, 0,info_head + info_body)
        else:
            win.attron(curses.color_pair(2))
            win.addstr(y_info, 0, warn)
            win.attroff(curses.color_pair(2))
            
        
        # win.addstr(y_split, 0, '•'*width)
        win.attron(curses.color_pair(4))
        win.addstr(y_input, 0, input_head)
        win.attroff(curses.color_pair(4))
        win.addstr(y_input, len(input_head), raw_input)
        
        
        win.refresh()

        ch = win.getch()
        if ch == -1:
            continue
        
        # _ch = ch
        ch = curses.keyname(ch).decode("utf-8")
        # cmds=[ch + " " +str(_ch)]
        win.clear()
        
        # Backspace
        if ch == "^H":
            raw_input=raw_input[:-1]
            continue
        # Enter
        elif ch != "^J":
            raw_input += ch
            continue
        
        # Handling raw_input
        
        raw_input = raw_input.strip()
        warn = None
        
        if raw_input.find("quit()") >=0:
            exit_flag=True
            if puber:
                puber.stop.set()
            
        args = raw_input.split()
        
        raw_input = ""
        
        if len(args)>1:
            chstat, args = args[0].upper(), args[1:]
        elif len(args)==1:
            chstat, args = args[0].upper(), None
        else:continue
        
        if chstat not in JUMP_TAB.keys():
            continue
        elif chstat not in JUMP_TAB[cur_stat] and chstat != cur_stat:
            warn = f"{cur_stat} can not change into {chstat}"
            continue
        
        # @ayx
        if chstat=="RECORD":
            if not args:
                warn=f"CMD {chstat} need listname"
                continue
            # new_path_list(args[0])
            pass
        elif chstat=="ADD":
            comment = args if args else ""
            # add_cur_loc(comment)
            pass
        elif chstat=="INSERT":
            pass
        elif chstat=="DELETE":
            pass
        elif chstat=="NAV":
            if not args or len(args)<2:
                warn=f"CMD {chstat} need dir and listname"
                continue
            dir,listname = args[0], args[1]
            puber = Naver(dir, listname)
            puber.start()
            pass
        elif chstat=="MVTO":
            pass
        elif chstat=="IDLE":
            if puber:
                # This only stop automatic nav command
                puber.stop.set()
                
                # Stop signal send need
                # send_stop_cmd()
            pass
        
        cur_stat = chstat
        
        win.refresh()
        win.clear()
        

def main(win):
    
    setup(win)
    
    height, width = win.getmaxyx()
    
    frame_welcome(win,height, width)
    
    main_loop(win,height, width)
   
    
    
    
curses.wrapper(main)

# pub = GTpub(path_list=list(range(3)))
# pub.start()
# print("123123123")