# Stand-alone file for the Brython code
#   easier to edit
#
from browser import document as doc

# Import local 'generic/standard Python' module
# The HTML5 file should be served (if running locally, use localhost
# as server, e.g.
# 
#   $ php -S localhost:8080
#
from cpc_random32 import randomize0, rnd

# GLOBALS
canvas = doc['plotarea']
ctx = canvas.getContext('2d')
console = doc['console']
scoreboard = doc['score']

borcol = '#ff0000' # cell border color
filcol = '#000000' # (empty) cell fill color
pcol = [filcol, '#0000ff','#ffff00'] # players' colors (0 = empty, 1 = player 1, 2 = player 2)

offx = 40
offy = 40
l1 = 50
l2 = 2
l3 = 8

def console_write(s):
    console.value += s
    
def console_clear():
    console.value = '(console cleared)\n'
    
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
    
    
draw_rectangle(offx, offy, 8*l1 + 2*l2, 8*l1 + 2*l2, borcol)
for iy in range(8):
    for ix in range(8):
        draw_cell(ix, iy, 0)

draw_cell(3,3,1)
draw_cell(4,4,1)
draw_cell(3,4,2)
draw_cell(4,3,2)
scoreboard.innerText = "2 : 2"

def canvas_click(ev):
    x = ev.offsetX
    y = ev.offsetY
    console_write('x: {0:d} y: {1:d}\t'.format(x,y))
    ix, iy, valid = get_cellcoord(x,y)
    console_write('ix: {0:d} iy: {1:d} {2}\n'.format(ix,iy, valid))
    console_write('    random: {0:f}\n'.format(rnd(1)))

def run_main_program(ev):
    console_clear()
    console_write('running random number test program...\n\n')
    randomize0()
    for i in range(10):
        console_write('{0}\t{1}\n'.format(i,rnd(1)))
    
    
canvas.bind('dblclick', canvas_click)
doc['btn-run'].bind('click', run_main_program)

# The `<=` operator is Brython-specific syntax shortcut.
# see: https://brython.info/static_tutorial/en/index.html#item0
#  
doc <= "Ready"
