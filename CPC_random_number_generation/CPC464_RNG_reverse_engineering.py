"""
Python port of reverse-engineered random number generator from Amstrad ROM
floating point routines

with claude.ai

261031 First version, still in need of tweaks and verification. In 
       particular, the random value returned by CPC BASIC is probably
       the value prior to calculation of the next number.


## From ROM disassembly

The RNG is the group of entries in the maths jumpblock at &BD97-&BDA0:

Jumpblock	ROM address	Function
&BD97	&2F94	Load the default seed
&BD9A	&2FA1	RANDOMIZE: reset to default seed, then XOR the argument’s 
                4 mantissa bytes into it
&BD9D	&2FB7	RND: advance the seed, then return it as a float
&BDA0	&2FE6	RND0: return the current seed without advancing

The 32-bit state lives at &B8E4-&B8E7, as two 16-bit words.


## About the Amstrad CPC RNG

The Amstrad CPC RNG is a 32-bit linear congruential generator whose 
multiplier is &6C078965 (1812433253, the same constant Knuth’s and the 
Mersenne Twister’s seeding recurrences use). The increment is the same
constant, so the intended update is seed = seed * &6C078965 + &6C078965.
The default seed is &89656C07. The output is the 32-bit seed used as a
mantissa with exponent &80, so the value is seed / 2^32.

It isn’t a correct 32-bit multiply

The routine builds the product from 16×16 partial products. A correct
multiply needs the low word of (seed_low × &6C07) for the cross term, but 
the code uses seed_high × &6C07 instead. The new high word comes out as 
hi16(lo×&8965) + lo16(hi×&8965) + lo16(hi×&6C07) + &6C07 + carry.

The low word still evolves as a proper 16-bit LCG. The 32-bit state as a 
whole is not a true LCG.
"""

import math

class CPCRnd:
    """Amstrad CPC464 firmware RND (floating point package, ROM &2F94-&2FF7)."""
    MLO, MHI = 0x8965, 0x6C07          # multiplier &6C078965, also used as the increment

    def __init__(self):
        self.reset()

    def reset(self):
        """Default seed (&2F94): (&B8E6)=&8965, (&B8E4)=&6C07 -> 32-bit state &89656C07."""
        self.lo = self.MHI              # word at &B8E4
        self.hi = self.MLO              # word at &B8E6

    @property
    def state(self):
        return self.lo | (self.hi << 16)

    def next_int(self):
        """Advance the seed (&2FB7) and return the 32-bit state."""
        lo, hi = self.lo, self.hi
        p1 = (hi * self.MHI) & 0xFFFF           # only low word kept
        p2 = lo * self.MLO                      # full 32-bit product
        p3 = (hi * self.MLO) & 0xFFFF           # only low word kept
        t = (p2 & 0xFFFF) + self.MLO
        self.lo = t & 0xFFFF
        self.hi = (p3 + self.MHI + (t >> 16) + (p2 >> 16) + p1) & 0xFFFF
        return self.state

    def rnd(self):
        """BASIC RND: advance, then seed / 2**32."""
        return self.next_int() / 2**32

    def rnd0(self):
        """BASIC RND(0): last value, no advance."""
        return self.state / 2**32

    def randomize(self, x=None):
        """RANDOMIZE x (&2FA1): reset to the default seed, then XOR the mantissa
        bytes of x (CPC 5-byte float, bytes 0..3 little-endian) into the state,
        unless x is zero."""
        self.reset()
        if x:
            s = self.state ^ cpc_float_mantissa(float(x))
            self.lo, self.hi = s & 0xFFFF, s >> 16


def cpc_float_mantissa(x):
    """32-bit mantissa word of x in the CPC float format
    (bit 31 = sign, implicit leading 1 dropped)."""
    m, _ = math.frexp(abs(x))                   # 0.5 <= m < 1
    mant = int(round(m * 2**32))
    if mant >= 2**32:                           # rounding overflow
        mant >>= 1
    mant &= 0x7FFFFFFF
    if x < 0:
        mant |= 0x80000000
    return mant


if __name__ == "__main__":
    r = CPCRnd()
    for _ in range(5):
        print(f"{r.rnd():.9f}")
        
        