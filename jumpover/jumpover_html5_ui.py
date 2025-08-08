from browser import document as doc
import browser.timer

import sys

import jumpover_core



####################################################
#
# game and program status globals
# 


PROGRAM_INIT = 0
WAIT_GAME_SETTINGS = 8
GAME_INIT = 16
WAIT_NEW_PLAYER_MOVE = 20 # 
WAIT_PLAYER_MOVE = 24 # if input invalid
DO_PLAYER_MOVE = 32
WAIT_COMPU_MOVE = 40
DO_COMPU_MOVE = 48

program_status = PROGRAM_INIT


# GLOBALS

borcol = '#f30506' # cell border color (CPC red)
filcol = '#000201' # (empty) cell fill color
pcol = [filcol, '#6e7bf6','#f3f30d'] # players' colors (0 = empty, 1 = player 1 CPC blue, 2 = player 2 CPC yellow)

# constants for drawing the board
offx = 40
offy = 40
l1 = 50
l2 = 2
l3 = 8



##################################################

# HTML5 UI elements

canvas = doc['plotarea']
ctx = canvas.getContext('2d')

console = doc['console']

scoreboard = doc['score']
scoreboard1 = doc['score1']
scoreboard2 = doc['score2']

radio_oneplayerY = doc['oneplayerY']
radio_oneplayerB = doc['oneplayerB']
radio_twoplayer = doc['twoplayer']
radio_noplayer  = doc['noplayer']

slide_strength = doc['strength']
viewstrength = doc['viewstrength']

# CPCrandom = doc['CPCrandom']
# viewCPCrandom = doc['viewCPCrandom']

Sobanski = doc['Sobanski']
viewSobanski = doc['viewSobanski']

button_yellow_start = doc['btn-yellow-starts']
button_blue_start = doc['btn-blue-starts']
button_stop = doc['btn-stop']
button_skip = doc['btn-skip']

computime_id = None # store computer move timer ID, set to 
                    #  None if no timer active
computime = 800    # delay (in milliseconds) to next computer move


# HTML5 UI functions

def console_write(s):
    console.value += s
    console.scrollTop = console.scrollHeight # autoscroll
    
def console_clear():
    console.value = ''
    console.scrollTop = console.scrollHeight # autoscroll
    
def draw_rectangle(x, y, dx, dy, col):
    ctx.beginPath()
    ctx.rect(x, y, dx, dy)
    ctx.fillStyle = col
    ctx.fill()

def draw_cell(ix, iy, ip):
    global l1, l2, l3, borcol, filcol, offx, offy
    y = iy * l1 + l2 + offy
    x = ix * l1 + l2 + offx
    draw_rectangle(x, y, l1, l1, borcol)
    draw_rectangle(x+l2, y+l2, l1-2*l2, l1-2*l2, filcol)
    draw_rectangle(x+l3, y+l3, l1-2*l3, l1-2*l3, pcol[ip])
    
def get_cellcoord(x, y):
    global l1, l2, l3, offx, offy
    rl = l3/l1
    valid_coord = False
    ix = round((x - offx - l2)/l1 - 0.5) 
    iy = round((y - offy - l2)/l1 - 0.5) 
    valid_coord = False
    # only validate coordinates if well within cell (l3 boundary)
    cx1 = ix * l1 + l2 + offx + l3
    cy1 = iy * l1 + l2 + offy + l3
    cx2 = cx1 + l1-2*l3
    cy2 = cy1 + l1-2*l3
    if (x >= cx1) and (x <= cx2) and (y >= cy1) and (y <= cy2):
        valid_coord = True
    #if valid_coord:
    #    result = (ix,iy)
    #else:
    #    result = None
    #return result
    return (ix, iy, valid_coord)
    
    
def startstop_buttons_gamemode(gameon):
    button_yellow_start.disabled = gameon
    if radio_twoplayer.checked or radio_noplayer.checked:
        button_blue_start.disabled = True
    else:
        button_blue_start.disabled = gameon
    button_stop.disabled = not gameon
    radio_oneplayerY.disabled = gameon
    radio_oneplayerB.disabled = gameon
    radio_twoplayer.disabled = gameon
    radio_noplayer.disabled = gameon
    slide_strength.disabled = gameon
    # CPCrandom.disabled = gameon
    Sobanski.disabled = gameon



def clear_compu_timer():
    global computime_id
    if not (computime_id is None):
        browser.timer.clear_timeout(computime_id) # does nothing if event already fired
        computime_id = None

def update_scoreboard():
    scoreboard1.innerText = '{0:2d}'.format(jumpover_core.cop)
    scoreboard2.innerText = '{0:2d}'.format(jumpover_core.spp)


# HTML5 UI event handlers

def canvas_click(ev):
    global program_status
    if program_status==WAIT_PLAYER_MOVE:
        x = ev.offsetX
        y = ev.offsetY
        # console_write('x: {0:d}   y: {1:d}\t'.format(x,y))
        ix, iy, valid_coords = get_cellcoord(x,y)
        # console_write('ix: {0:d} iy: {1:d} {2}\n'.format(ix,iy, valid_coords))
        if valid_coords:
            exec_player_move(iy+1, ix+1)
        update_scoreboard()
    else:
        console_write("Not your turn yet!\n")
    

def skip_click(ev):
    global program_status
    if program_status==WAIT_PLAYER_MOVE:
        exec_player_move(0, 0) # 0,0 means skip move
        update_scoreboard()
    else:
        console_write('ERROR: SKIP TURN should not be active\n')
        
        
def exec_player_move(iy1, ix1):
    set_prog_status(DO_PLAYER_MOVE)
    result,msg = jumpover_core.spielers_zug(iy1, ix1)
    console_write('spielers_zug result = '+result+'\t')
    console_write('msg = '+msg+'\n')
    if result in ['OK', 'SKIP TURN']:
        set_prog_status(WAIT_COMPU_MOVE)
    elif result in ['TWO PLAYER GAME','TWO PLAYER GAME SKIP TURN']:
        set_prog_status(WAIT_NEW_PLAYER_MOVE)
    elif result == 'END GAME':
        stop_game('normal END GAME signal, msg = '+msg) # TO DO replace with set_prog_status
    else:
        set_prog_status(WAIT_PLAYER_MOVE)
        console_write(msg+'\n')     
     
     

def select_1pY(ev):
    engine_settings_hidden(False)
    button_yellow_start.disabled = False # TO DO: this may be removed, if working correctly
    button_blue_start.disabled = False
    jumpover_core.ANZAHL_SPIELER = 1
    jumpover_core.PLAYERCOLORCODE = 2 # 'blau' = 1 , 'gelb' = 2
    # console_write('selected 1 player (yellow)\n')

def select_1pB(ev):
    engine_settings_hidden(False)
    button_yellow_start.disabled = False # TO DO: this may be removed, if working correctly
    button_blue_start.disabled = False
    jumpover_core.ANZAHL_SPIELER = 1
    jumpover_core.PLAYERCOLORCODE = 1 # 'blau' = 1 , 'gelb' = 2
    # console_write('selected 1 player (blue)\n')

def select_2p(ev):
    engine_settings_hidden(True)
    button_yellow_start.disabled = False # set to true if not working (TODO: implement that yellow can start game)
    button_blue_start.disabled = True
    jumpover_core.ANZAHL_SPIELER = 2
    jumpover_core.PLAYERCOLORCODE = 2 # yellow starts is default
    # console_write('selected 2 player\n')
    
def select_0p(ev):
    engine_settings_hidden(False)
    button_yellow_start.disabled = False
    button_blue_start.disabled = True
    jumpover_core.ANZAHL_SPIELER = -1
    # console_write('selected no player\n')
    
def engine_settings_hidden(b):
    slide_strength.disabled = b
    viewstrength.hidden = b
    # viewCPCrandom.hidden = b
    viewSobanski.hidden = b



def go_yellow(ev):
    start_game('YELLOW')
    
def go_blue(ev):
    start_game('BLUE')

def stop(ev):
    stop_game('USER_BREAK')




def do_compu_move():
    """do computer move
    
    only called via set_timeout
    """
    global computime_id

    computime_id = None 
    set_prog_status(DO_COMPU_MOVE)
    
    assert jumpover_core.anz_sp != 2,\
        "In two-player mode, this code should never be reached!"
    
    result,msg = jumpover_core.computers_zug()
    console_write('computers_zug result = '+result+'\t')
    console_write('msg = '+msg+'\n')
    
    gameon = True
    human_player = True
    crash = False
    if (result=='SKIP TURN'):
        if (jumpover_core.anz_sp == -1):
            if jumpover_core.STRICT_SOBANSKI: 
                console_write('STRICT SOBANSKI STATUS!!\n')
                human_player = True
            else:
                human_player = False
        elif (jumpover_core.anz_sp == 1):
            human_player = True
        else:
            crash = True
            crashmsg = 'incompatible number of players!'
    elif (result=='OK'):
        human_player = True
    elif (result=='ZERO PLAYER GAME'):
        human_player = False
    elif (result=='END GAME'):
        gameon = False
    else:
        crash = True
        crashmsg = "CRASH: unknown 'result' from computers_zug!"

    update_scoreboard()

    # Which function to call next?
    # any follow-up calls should be placed here, at the end of the 
    # function, not in the earlier function body
    # Only one follow-up should be called, and this should be the last
    # thing that this function does
    if crash:
        console_write('CRASH: '+crashmsg+'\n')
        raise Exception('program crashed in do_compu_move')
        stop_game('PROGRAM CRASHED')
    else:
        if not gameon:
            stop_game('normal END GAME signal, msg = '+msg)
        else:
            if human_player:
                set_prog_status(WAIT_NEW_PLAYER_MOVE)
            else:
                set_prog_status(WAIT_COMPU_MOVE)


    
#########################################
#
# PROGRAM and GAME LOGIC
#
###########################################



def set_prog_status(new_status):
    """set program/game status
    
    
    PROGRAM_INIT = 0
    WAIT_GAME_SETTINGS = 8
    GAME_INIT = 16
    WAIT_NEW_PLAYER_MOVE = 20 # 
    WAIT_PLAYER_MOVE = 24 # if input invalid
    DO_PLAYER_MOVE = 32
    WAIT_COMPU_MOVE = 40
    DO_COMPU_MOVE = 48
    
    """
    
    
    #TODO? we could check old_status here and detect any forbidden
    #      state transition (debugging)
    global program_status
    global computime_id, computime
    
    if new_status == PROGRAM_INIT:
        program_status = PROGRAM_INIT
        button_skip.disabled = True
    elif new_status == WAIT_GAME_SETTINGS:
        program_status = WAIT_GAME_SETTINGS
        startstop_buttons_gamemode(False)
        button_skip.disabled = True
        console_write('Please select your game settings on top of the '\
                      'screen.\nAfterwards, push either "Gelb fängt an" '\
                      '(yellow begins) or "Blau fängt an" (blue begins) '\
                      'to start the game.\n')
    elif new_status == GAME_INIT:
        program_status = GAME_INIT
        startstop_buttons_gamemode(True)
        button_skip.disabled = True
    elif new_status == WAIT_NEW_PLAYER_MOVE:
        program_status = WAIT_NEW_PLAYER_MOVE
        button_skip.disabled = False
        jumpover_core.spielers_zug_vorbereiten()
        program_status = WAIT_PLAYER_MOVE 
    elif new_status == WAIT_PLAYER_MOVE:
        button_skip.disabled = False
        if jumpover_core.anz_sp == -1:
            console_write('***WARNING: zero-player mode has switched to human player***\n')
            console_write('This has been done for compatibility with original JUMP OVER\n\n')
        program_status = WAIT_PLAYER_MOVE
    elif new_status == DO_PLAYER_MOVE:
        program_status = DO_PLAYER_MOVE
        button_skip.disabled = True
    elif new_status == WAIT_COMPU_MOVE:
        program_status = WAIT_COMPU_MOVE
        computime_id = browser.timer.set_timeout(do_compu_move, computime)
        button_skip.disabled = True
    elif new_status == DO_COMPU_MOVE:
        program_status = DO_COMPU_MOVE
        button_skip.disabled = True
    else:
        console_write('CRASH: undefined program state! Check browser'\
                      ' logs.\n')
        raise Exception('program crashed in set_prog_status')
        button_skip.disabled = True
        stop_game('PROGRAM CRASHED')



def start_game(startcolor):
    console_write('GO '+startcolor+'!\n')
    console_write('To place your piece, double-click in the desired square.\n')
    set_prog_status(GAME_INIT)
    

   
    # get game parameters from UI
                  
    if radio_oneplayerY.checked:
        jumpover_core.ANZAHL_SPIELER = 1
        jumpover_core.PLAYERCOLORCODE = 2
    elif radio_oneplayerB.checked:
        jumpover_core.ANZAHL_SPIELER = 1
        jumpover_core.PLAYERCOLORCODE = 1
    elif radio_twoplayer.checked:
        jumpover_core.ANZAHL_SPIELER = 2
        jumpover_core.PLAYERCOLORCODE = 2 # for correct starting color logic
    elif radio_noplayer.checked:
        jumpover_core.ANZAHL_SPIELER = -1
        #??? jumpover_core.PLAYERCOLORCODE = ???
        
    jumpover_core.SPIELSTAERKE = int(slide_strength.value)

    # assert type(CPCrandom.checked)==bool, 'CPCrandom.checked not a boolean'
    assert type(Sobanski.checked)==bool, 'Sobanski.checked not a boolean'
    # jumpover_core.CPC_RANDOM = CPCrandom.checked
    # there is now only one checkbox (Sobanski), which handles both 
    # the CPC random status and the Sobanski compatibility
    jumpover_core.CPC_RANDOM = Sobanski.checked 
    jumpover_core.STRICT_SOBANSKI = Sobanski.checked
    
    # this is for 1p (2p?)
    if jumpover_core.PLAYERCOLORCODE==2: 
        # 1p: player has yellow
        jumpover_core.PLAYERFIRST = (startcolor == 'YELLOW') 
    else:
        # 1p: player has blue (and will start if startcolor == 'BLUE')
        jumpover_core.PLAYERFIRST = (startcolor == 'BLUE') 

    # reset timer
    clear_compu_timer()
    
    # disable 'Zug abgeben' button (only enabled when in WAIT_PLAYER_MOVE mode)
    button_skip.disabled = True
    
    # initialize new game
    jumpover_core.newgame_init()
    
    # set scoreboard colors
    # and update score
    if (jumpover_core.anz_sp == -1): # 0 player game (yellow begins)
        scoreboard1.style.color = pcol[2]
        scoreboard2.style.color = pcol[1]
    elif (jumpover_core.anz_sp == 2): # 2 player game (yellow begins)
        scoreboard1.style.color = pcol[1]
        scoreboard2.style.color = pcol[2]
    else:
        if jumpover_core.PLAYERCOLORCODE==2:
            scoreboard1.style.color = pcol[1]
            scoreboard2.style.color = pcol[2]
        else:
            scoreboard1.style.color = pcol[2]
            scoreboard2.style.color = pcol[1]

        
    update_scoreboard()
    
    
    # decide which status to set first
    # the play logic will probably need some GLOBAL status variables
    # (see jumpover_core)
    # there are some status set functions that enable, disable certain
    #  event handlers
    
    # game loop prelude
    if jumpover_core.anz_sp == 1:
        if jumpover_core.PLAYERFIRST:
            human_player = True
        else:
            human_player = False
    elif jumpover_core.anz_sp == 2:
        human_player = True
    elif jumpover_core.anz_sp == -1:
        human_player = False
    else:
        raise Exception('jumpover_core.anz_sp ungueltig')

    if human_player:
        set_prog_status(WAIT_NEW_PLAYER_MOVE)
    else:
        set_prog_status(WAIT_COMPU_MOVE)
   
    

def stop_game(reason):
    console_write('STOP (reason: '+reason+')\n')
    console_write("Switching program state to 'WAIT_GAME_SETTINGS'\n")
    console_write("TO DO: create separate function handler for program crash (unclosable modal window forcing manual page reload?)\n")
    set_prog_status(WAIT_GAME_SETTINGS)
    # probably create a separate function for reason == PROGRAM CRASH
 


######################################################"
# program initialization

set_prog_status(PROGRAM_INIT)




###########################################################
# configure jumpover_core to work with HTML5 user interface
############################################################

#
# overload 'text-mode' UI_draw_field routine
# with HTML5 version
#
def HTML_draw_field(re, se, ds):
    # row, col indexing is shifted by one in the HTML draw_cell
    # also se => x, re => y
    draw_cell(se-1, re-1, ds)
    
jumpover_core.UI_draw_field = HTML_draw_field

#
# overload 'text-mode' show board status routine
# with HTML5 version
#
def HTML_display_board():
    pass
    
jumpover_core.UI_display_board = HTML_display_board




#####################################################################
# explicitly set all UI buttons/sliders and the corresponding
# program variables on program start (needed only once)

# select single player
jumpover_core.ANZAHL_SPIELER = 1 # can be -1 (computer vs computer), 1, 2
jumpover_core.PLAYERCOLORCODE = 2 # 'blau' = 1 , 'gelb' = 2
jumpover_core.PLAYERFIRST = True # should player start?
radio_noplayer.checked = False
radio_twoplayer.checked = False
radio_oneplayerB.checked = False
radio_oneplayerY.checked = True
engine_settings_hidden(False)

# select strength = 1
jumpover_core.SPIELSTAERKE = 1 # can be 1, 2, 3, 4
slide_strength.value = jumpover_core.SPIELSTAERKE

# CPCrandom mode
jumpover_core.CPC_RANDOM = True # use CPC random generator clone
# CPCrandom.checked = jumpover_core.CPC_RANDOM

# Sobanski mode
jumpover_core.STRICT_SOBANSKI = True # this affects zero-player mode 
                           # ending "KANN NICHT ZIEHEN"
Sobanski.checked = jumpover_core.STRICT_SOBANSKI

# Buttons enabled/disabled (initial state)
startstop_buttons_gamemode(False)
# disable 'Zug abgeben' button (only enabled when in WAIT_PLAYER_MOVE mode)
button_skip.disabled = True


# initialize score-board
scoreboard1.innerText = '?'
scoreboard1.style.color = pcol[2]
scoreboard2.innerText = '?'
scoreboard2.style.color = pcol[1]

# clear console
console_clear()

# reset timer (not really necessary, but for good habit)
clear_compu_timer()



#######################################################
#
# initialization: draw board (needed only once)
# TO DO include ROW/COLUMN numbers
draw_rectangle(offx, offy, 8*l1 + 2*l2, 8*l1 + 2*l2, borcol)

# this clears all cells (on screen, not in field status matrix)
# we can do this here once, to obtain a nice board
for iy in range(8):
    for ix in range(8):
        draw_cell(ix, iy, 0)


############################################
# 
# set up fresh board

jumpover_core.setup_fresh_board()
update_scoreboard()


    
##########################
#
# UI event bindings (only bind events AFTER properly initializing all buttons)
#
##########################

canvas.bind('dblclick', canvas_click)
button_skip.bind('dblclick', skip_click)

button_yellow_start.bind('click', go_yellow)
button_blue_start.bind('click', go_blue)
button_stop.bind('click', stop)

radio_oneplayerY.bind('click', select_1pY)
radio_oneplayerB.bind('click', select_1pB)
radio_twoplayer.bind('click', select_2p)
radio_noplayer.bind('click', select_0p)


# ALL PROGRAM INITIALIZATION DONE

console_write('Python '+sys.version+'\n\n')

# switch program status to "waiting for game settings"
set_prog_status(WAIT_GAME_SETTINGS)


#####################################################################

############################################
###
### Programming snippets for debugging etc.
###
############################################

## investigate objects
#
# for ln in dir(scoreboard1):
#     console_write(ln+'\n')

## The `<=` operator is Brython-specific syntax shortcut.
## see: https://brython.info/static_tutorial/en/index.html#item0
# 
# doc <= "Ready"
