# HTML5 port of Sobanski's "Jump Over"

This is a port (still under development) in HTML5/JavaScript/Brython of the wonderful "Jump Over" game that was programmed by Bodo Sobanski in Locomotive Basic for the Amstrad/Schneider CPC464 (and related computers). This port is an adaptation that aims mainly to preserve the computer's strategy and game play. The original code can be found in *CPC Magazin* **1986/02**, pp. 71-76 (see ``./documentation/``).


## Running the program

This HTML5 game is intended to be included on a web server. Everything is in the ``./jumpover/`` directory.

The program can be run locally using a local web server. For example,

```bash
$ python -m http.server --directory ./jumpover/ 8080
 
```

and then open a web browser on http://localhost:8080.

## Development notes

There is more background information in the ``./documentation/`` directory.

A particularity of the present port is that a specific random generator was programmed that perfectly reproduces the random number sequence from the Amstrad/Schneider CPC464/664/6128 Locomative Basic floating point code. This was needed, such that the Jump Over port exactly reproduces the computer strategy from the Amstrad/Schneider version. In the HTML5 game, this is called "Pure Sobanski CPC" mode.  







