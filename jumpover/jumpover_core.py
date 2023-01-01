# JUMP OVER
#
# Python port of Bodo Sobanski's "Jump Over" BASIC program
# originally written for the Amstrad/Schneider CPC464 (Locomotive Basic)
#
# by Marty Valentine, 2020-2021
#
# 
# This `jumpover_core.py` is the core code. It can still be run from the
# command line (thanks to the `if (__name__=='__main__'):` construct),
# but is mainly intended to be imported as a module by the main
# Brython code.
#
#
# The original Basic program was published in 
# 'CPC Magazin 1986-02 (Februär)', pages 72-76
# published by Verlag Rätz-Eberle (Bretten, Germany)
#
# As source, I used a digitally available version of the Amstrad Basic
# program, which unfortunately does not have the same line numbering as
# the published paper source.
# 

#
# Other browser adaptations of Othello/Reversi/Jump Over
#   https://ogeon.github.io/reversi/
#       https://github.com/Ogeon/reversi
#
# TODO: clean up a bit, but keep diagnostics for now
# TODO: debug infinite loop in autoplay (perhaps already fixed?)


import random
from cpc_random32 import randomize0
from cpc_random32 import rnd

#
# Unexpected hurdles in porting the code
# ======================================
#
# The original code (with random numbers initialized using
# RANDOMIZE zv (where zv is not initialized and thus evaluates to 
# `RANDOMIZE 0`)
# systematically yields 31-32 score in autoplay with "kann nicht ziehen".
# If we skip this turn, and do "*break" "ks=0" "cont"
#  we can go to the end of the game, with score 38:26
#
# The reason that the 31-32 is reproducible comes from the random seed
# which gives always the same sequence of moves...
# if we change the line with RANDOMIZE ZV into RANDOMIZE 0.3
# in the original Amstrad CPC code
# we get 31:33 score!! (and no "kann nicht ziehen")
#
# Running the Python code here, with randomly-seeded psueudo random 
# numbers many times, sometimes we do get the 38:26 final score
# also we get 31:33 sometimes etc.
# sometimes we get infinite loop... (this has to do with 
# "kann nicht ziehen", I think, the "ks" does not behave correctly)

# To really reproduce all behaviour of the original Amstrad program
# running on the Amstrad, we have dont the following:
#  => use random number generator from amstrad!! => OK: see cpc_random32
#  => switch to 'user move' for the first 'kann nicht ziehen' 
#     in zeroplayer mode
#           


# Debug settings (needs console)

DIAGNOSTIC_MODE = False # output a whole lot of information for checking
                       # each and every step of the program
ULTRA_DIAGNOSTIC = False # set this to False to reduce a bit the output
                         # of DIAGNOSTIC_MODE
STEP_MODE = False # wait after each move ('press ENTER to continue')



# Diagnostics (kind of logging)


def diagnostics(s):
    if DIAGNOSTIC_MODE:
        print(s)


# pre-define global module variables
# (will be initialized again in newgame_init)

cop = 2
spp = 2
az = 4
ks = 0
ds = 0 


#
# SET UP GAME: fixed tables and subroutines
#

# color name look-up table
farbe = ['leer','blau','gelb']

# array indexing in Sobanski code: 0-based
# this implies that some elements are implicitly initialized with 0
# array indexing here: 0-based
# here, we need to explicitly specify the 0 elements

# koordinaten fuer rundumpruefung
rr = [0,    0, -1, -1, -1,  0,  1, 1, 1, 0]
sr = [0,    1,  1,  0, -1, -1, -1, 0, 1, 0]

# sonderpunkte-tabelle fuer spielstaerke 3 und 4
spf = [[0,   0,   0,   0,   0,   0,   0,   0,   0, 0],
       [0,2800, 500, 900, 950, 950, 900, 500,2800, 0],
       [0, 500,   0, 785, 785, 785, 785,   0, 500, 0],
       [0, 900, 785, 805, 801, 801, 805, 785, 900, 0],
       [0, 950, 785, 801, 801, 801, 801, 785, 950, 0],
       [0, 950, 785, 801, 801, 801, 801, 785, 950, 0],
       [0, 900, 785, 805, 801, 801, 805, 785, 900, 0],
       [0, 500,   0, 785, 785, 785, 785,   0, 500, 0],
       [0,2800, 500, 900, 950, 950, 900, 500,2800, 0],
       [0,   0,   0,   0,   0,   0,   0,   0,   0, 0]]

# spielfeld-matrix

sf = [[0 for i in range(10)] for j in range(10)]


###############################################################
# UI subroutines (connection to graphical output)
#
# These are typically called by the Jump Over main code
# when the original draws something onto the screen or expects
# user input.
###############################################################
def UI_draw_field(re, se, ds):
    global DIAGNOSTIC_MODE
    global ULTRA_DIAGNOSTIC

    if DIAGNOSTIC_MODE:
        print('UI_draw_field: ', re, se, ds)
        if ULTRA_DIAGNOSTIC:
            UI_display_board()
    #
    # 5200 PEN #1, DS
    # 5210 FOR N2=1 TO 2
    # 5220  LOCATE #1, SG, RG-1+N2
    # 5230  PRINT #1, CHR$(143);CHR$(143);
    # 5240 NEXT N2
    # 5250 RETURN    


def UI_display_board():
    global sf
    
    print('      ', end='')
    for s in range(10):
        print(' (C{0:1d})'.format(s), sep = '',
              end='')
    print('')
    for r in range(10):
        print('(R{0:1d})'.format(r), end='')
        for s in range(10):
            print('{0:5d}'.format(sf[r][s]), sep = ' ',
                  end='')
        print('')
    print('-'*60)


def UI_display_score():
    global cop
    global spp
    
    print('score: COP =',cop, ' - SPP =',spp) 





###############################################################
# Jump Over main code: subroutines
###############################################################
def sub_feld_faerben(re, se, ds):
    global sf

    #line 5170 
    # rg = (re*3)-1 #NOT NEEDED
    # sg = (se*3)-1 #NOT NEEDED
    sf[re][se] = ds
    #line 5200
    UI_draw_field(re, se, ds)



def sub_test_nachbarfeld(r, s):
    global sf, dg
    found = False
    for rv in range(-1,2):
        for sv in range(-1,2):
            if sf[r+rv][s+sv] == dg:
                found = True
                break
        if found:
            break
    return found


def sub_zaehlen_updaten(r, s, us):
    #TODO update globals list
    global cop,spp
    global az,ks
    epz = 0
    spz = 0
    # line 4750
    # von der derzeitigen position aus
    # wird in allen 8 richtungen auf 
    # gegner geprueft
    for n in range(1,9):
        re = r + rr[n]
        se = s + sr[n]
        vsr = 0 #instead of sr which is already an array!!
        spr = 0
        if sf[re][se]!=dg:
            # GOTO 5110
            continue
        #line 4860
        # ermittelte richtung wird auf
        # weitere gegner untersucht
        doloop = True
        while doloop:
            # line 4900
            vsr = vsr + 1
            spr = spr + spf[re][se]
            re = re+rr[n]
            se = se+sr[n]
            if sf[re][se] == ds:
                doloop=False
            if sf[re][se] == 0:
                doloop=False
        if sf[re][se] == 0:
            continue
            # GOTO 5110
        #line 4970
        epz = epz + vsr
        spz = spz + spr
        if not us:
            # GOTO 5110
            diagnostics('US False')
        else:
            #line 5000
            # update spielfeld
            re = r
            se = s
            diagnostics('VSR={0}'.format(vsr))
            for n1 in range(0, vsr+1):
                #TODO: SOUND!!
                sub_feld_faerben(re, se, ds)
                re = re+rr[n]
                se = se+sr[n]
            #line 5100
            #NEXT N1
    #line 5110
    #NEXT N
    if (spz>0):
        spz=spz+spf[r][s]
    return epz, spz


def computers_zug():
    #TODO: update globals list
    # try to make variables local
    # and/or pass them as parameters
    # return values
    global farbe
    global anz_sp
    global ds, co, sp, dg
    global cop,spp
    global az,ks
    if (anz_sp == -1) and (ds == co):
        ds = sp
        dg = co
        # GOTO 2700
    else:
        ds = co
        dg = sp
    #line 2700
    pz = -1
    br = 0
    bs = 0
    # PEN#0,ds
    # PEN#6,ds
    #line 2750
    # suche nach einem freien feld
    for r in range(1,9):
        for s in range(1,9):
            diagnostics('S LOOP r={0} s={1}'.format(r,s))
            if (sf[r][s] > 0):
                # GOTO 3200
                diagnostics('occupied GOTO 3200')
                continue
            nv = sub_test_nachbarfeld(r,s) # returns nv
            if nv == False:
                # GOTO 3200
                diagnostics('no neighbor GOTO 3200')
                continue
            #GOSUB 4730
            epz, spz = sub_zaehlen_updaten(r, s, False)
            if epz == 0:
                # GOTO 3200
                diagnostics('illegal move GOTO 3200')
                continue 
            assert type(r)==int, 'r should be int'
            assert type(s)==int, 's should be int'
            if st==2:
                #line 3010
                if ((r-1)*(r-8)) == 0:
                    epz = epz + st
                if ((s-1)*(s-8)) == 0:
                    epz = epz + st               
            elif st==3:
                epz = epz + spf[r][s]
                # GOTO 3080
            elif st==4:
                epz = epz + spz
                # GOTO 3080
            #line 3080
            betterscore = False
            if (epz>pz):
                betterscore = True
            elif epz==pz:
                #line 3100
                if CPC_RANDOM:
                    zv = rnd(1)
                else:
                    zv = random.random()
                #zv = 0.6 #DEBUG!!! TODO remove
                if zv<0.5:
                    betterscore = True
            # line 3180
            if betterscore:
                pz = epz
                br = r
                bs = s
            diagnostics('S LOOP END LOOP')
        #line 3200 NEXT S
    #line 3210 NEXT R
    if not (pz > 0):
        #line 3300
        #TODO sound
        # print('ICH KANN NICHT ZIEHEN')
        if ks==1:
            #...THEN 4420
            return ('END GAME','Ich kann nicht ziehen')
        else:
            ks = 1
        #line 3340 GOTO 3670 ('spieler's zug')
        return ('SKIP TURN','Ich kann nicht ziehen.')
    #line 3380
    ks = 0
    # PRINT CHR$(245)+" "+CHR$(241)+"  :  "+
    # MID$((STR$(BR),2,2)+MID$((STR$(BS)),2,2)
    # print('[Compu]['+farbe[ds]+'] ', end='')
    # print('RC:{0:d}{1:d}'.format(br,bs))
    diagnostics('PZ = {0}'.format(pz))
    # CLS#6
    r = br
    s = bs
    # GOSUB 4730
    epz, spz = sub_zaehlen_updaten(r, s, True)
    if (anz_sp == -1) and (ds == sp):
        spp = spp + epz + 1
        cop = cop - epz
        # GOTO 3480
    else:
        cop = cop + epz + 1
        spp = spp - epz
    #line 3480
    az = az + 1
    # spielstand updaten (TODO, UI?)
    #line 3520
    #print('COP =',cop, ' - SPP =',spp)
    if (spp == 0) or (cop == 0):
        return ('END GAME','spp==0 or cop==0')
    if az == 64:
        return ('END GAME','az==64')
    #IF AS=2 THEN 3670
    if anz_sp == -1:
        return ('ZERO PLAYER GAME','')
    else:
        return ('OK','')




def spielers_zug_vorbereiten():
    global farbe
    global anz_sp
    global ds, co, sp, dg
    global cop,spp
    global az,ks

    # the anz_sp==-1 case was added for compatibility with strict sobanski
    # (this leads to switching players when last computer move leads 
    # to "Ich kann nicht ziehen")
    if ((anz_sp==2) or (anz_sp==-1)) and (ds==sp):
        ds = co
        dg = sp
        # GOTO 3700
    else:
        ds = sp
        dg = co




def spielers_zug(R_IN = None, S_IN = None):
    global farbe
    global anz_sp
    global ds, co, sp, dg
    global cop,spp
    global az,ks

    quitgame = False
    skipmove = False
    if R_IN is None:
        # INPUT R,S
        
        #line 3700
        # PEN #0,DS
        # PEN #6,DS
        # PRINT CHR$(243)+" "+CHR$(241)+"  :  ";
        print('[Human]['+farbe[ds]+'] ', end='')
        inputloop = True
        while inputloop:
            rs = input("RC:")
            if rs.upper()=='E':
                quitgame = True
                inputloop = False
                break
            try:
                r = int(rs[0])
            except:
                r = 0
            try:    
                s = int(rs[1])
            except:
                s = 0
            if (r==0) and (s==0):
                astr = input("Geben sie diesen zug ab?")
                if astr.upper()=="J":
                    inputloop = False
                    skipmove = True
            else:
                inputloop = False
                if (r<1) or (r>8):
                    inputloop = True
                if (s<1) or (s>8):
                    inputloop = True
        if quitgame:
            return ('END GAME','')
        #line 3890
        # pruefen ob leer
    else:
        if R_IN==0:
            skipmove = True
        else:
            r = R_IN
            s = S_IN

    if skipmove:
        #TODO: check ks
        if ks==1:
            quitgame = True
            return ('END GAME','')
        else:
            ks = 1
            diagnostics('set ks = 1')
        #line 3870
        #IF AS=2 THEN 3670
        if anz_sp == 2:
            return ('TWO PLAYER GAME SKIP TURN','')
        else:
            return ('SKIP TURN','')        
        
    # OK:
    # valid values for r and s
    
    if not sf[r][s] == 0:
        #TODO SOUND
        # print("Feld ist besetzt")
        return ('INVALID MOVE',"Feld ist besetzt")
    #line 3960
    #  test ob gueltiger nachbar
    #line 3990
    nv = sub_test_nachbarfeld(r,s) # returns nv
    if not nv:
        #TODO SOUND
        # print("Nicht neben einem meiner Steine")
        return ('INVALID MOVE',"Nicht neben einem meiner Steine")
    #line 4040
    # test ob gueltiger zug
    #line 4070
    # GOSUB 4730
    epz, spz = sub_zaehlen_updaten(r, s, False)
    if not (epz > 0):
        #TODO SOUND
        #print("Zug ist ungueltig")
        return ('INVALID MOVE (retry)',"Zug ist ungueltig")
        
    #line 4130
    #  alles gueltig, zug durchfuehren
    #line 4160
    ks = 0
    # GOSUB 4730
    epz, spz = sub_zaehlen_updaten(r, s, True)
    if (anz_sp == 2) and (ds==co):
        cop = cop + epz + 1
        spp = spp - epz
        # GOTO 4220
    else:
        spp = spp + epz + 1
        cop = cop - epz
    #line 4220
    az = az + 1
    #line 4230
    # spielstand updaten
    #line 4260
    #TODO: spielstand updaten
    # print('COP =',cop, ' - SPP =',spp)   
    #line 4320
    # test ob spielende
    #line 4350
    if (spp == 0) or (cop == 0):
        return ('END GAME','')
    if az == 64:
        return ('END GAME','')
    #IF AS=2 THEN 3670
    if anz_sp == 2:
        return ('TWO PLAYER GAME','')
    else:
        return ('OK','')



def setup_fresh_board():
    global sf
    
    # reset spielfeld matrix (perhaps redundant)
    for r in range(10):
        for s in range(10):
            sf[r][s] = 0
            
    for r in range(1,9):
        for s in range(1,9):
            sub_feld_faerben(r, s, 0)

    #line 2430
    sub_feld_faerben(4, 5, 2)
    sub_feld_faerben(5, 4, 2)
    sub_feld_faerben(4, 4, 1)
    sub_feld_faerben(5, 5, 1)

    
def newgame_init():
    # First part of the game initialization

    global CPC_RANDOM
    global SPIELSTAERKE
    global ANZAHL_SPIELER
    global PLAYERCOLORCODE
    
    global anz_sp
    global co
    global sp
    global st
    
    global sf
    global cop
    global spp
    global az
    global ks
    global ds

    if CPC_RANDOM:
        randomize0()

    anz_sp = ANZAHL_SPIELER # Anzahl Spieler (AS)
    # if anz_sp == -1: computer plays itself
    if anz_sp == 2:
        co = 1  # Correct on 210808, if two_player then yellow begins
        sp = 2 
        # GOTO 1560
    else:
        st = SPIELSTAERKE # Spielstärke
        if (st < 1) or (st > 4):
            st = 4    
        if anz_sp == -1:
            co = 2
            sp = 1
            # GOTO 1560
        else:
            a = PLAYERCOLORCODE
            if a == 1:
                sp = 1
                co = 2
            else:
                sp = 2
                co = 1

    # second part of Jump Over initialization
    #line 1560
    # spielfeld initialisieren
    
    setup_fresh_board()
    
    UI_display_board()
    
    #line 2530
    cop = 2
    spp = 2
    az = 4
    ks = 0
    ds = 0 # initialization



###############################################################
# Jump Over main code: program
###############################################################

if (__name__=='__main__'):
    
    # set game parameters
    # TODO: get from user interface
    # TODO: make a function that does this using specific parameter arguments
    ANZAHL_SPIELER = -1 # can be -1 (computer vs computer), 1, 2
    SPIELSTAERKE = 2 # can be 1, 2, 3, 4
    PLAYERCOLORCODE = 2 # 'blau' = 1 , 'gelb' = 2 
    PLAYERFIRST = True # should player start?
    
    CPC_RANDOM = True # use CPC random generator clone
    STRICT_SOBANSKI = True # this affects zero-player mode 
                           # ending "KANN NICHT ZIEHEN"
                           
    # DIAGNOSTIC_MODE = True # switch to diagnostic mode


    # initializations
    newgame_init()


    # GAME LOOP (and prelude)
    
    # game loop prelude
    if anz_sp == 1:
        if PLAYERFIRST:
            human_player = True
        else:
            human_player = False
    elif anz_sp == 2:
        human_player = True
    elif anz_sp == -1:
        human_player = False
    else:
        raise Exception('anz_sp ungueltig')

    gameon = True
    while gameon:
        diagnostics('KS={0}'.format(ks))
        if human_player:
            #assert anz_sp != -1, "In zero-player mode, this code should never be reached!"
            if anz_sp == -1:
                print('***WARNING: zero-player mode has switched to human player***')
                print('This has been done for compatibility with original JUMP OVER')
                print('')
            playloop = True
            spielers_zug_vorbereiten()
            while playloop:
                status,msg = spielers_zug()
                if status in ['OK', 'TWO PLAYER GAME', 'SKIP TURN']:
                    playloop = False
                elif status == 'END GAME':
                    playloop = False
                    gameon = False
                else:
                    print(msg)
            if anz_sp == 1:
                human_player = False
        else:
            assert anz_sp != 2, "In two-player mode, this code should never be reached!"
            playloop = True
            while playloop:
                status,msg = computers_zug()
                if not (msg == ''):
                    print(msg)
                if status in ['OK', 'ZERO PLAYER GAME', 'SKIP TURN']:
                    playloop = False
                elif status == 'END GAME':
                    playloop = False
                    gameon = False
            if anz_sp == 1:
                human_player = True
            if STRICT_SOBANSKI:
                if (anz_sp == -1) and status=='SKIP TURN':
                    human_player = True
        UI_display_board()
        UI_display_score()
        if STEP_MODE:
            input('*** ENTER TO CONTINUE***')
    # -------
    # ENDE
    # --------
    #line 4420
    # TO DO: 'noch einmal?'
    print("PROGRAM ENDED")
