"""PyAV 18's view of a rational value, on PyAV 18 and 19 alike.

PyAV 19 changed every rational attribute - time_base, average_rate,
base_rate, guessed_rate, framerate, rate, sample_aspect_ratio,
display_aspect_ratio, on streams, codec contexts, packets and frames - from
`fractions.Fraction` (or None when unset) to its own `av.AVRational`, never
None: unset is a falsy AVRational(0, 1).  Arithmetic still works and returns
Fractions, but much does not, all measured on 19.0.1:

    x is None / x is not None   never true / always true, so an unset time
                                base is used where the code meant to fall back
    int(x), round(x)            TypeError
    "{:.2f}".format(x), "%d"    TypeError
    isinstance(x, Fraction)     False

A value usually travels through a variable before any of that happens
(`fps = stream.average_rate` ... `int(fps)` much later), so finding the
failures by searching is not reliable.  Instead every place that READS a
rational to compute with it, test it or format it goes through `q()`, which
returns exactly what PyAV 18 returned: a Fraction, or None when unset (18
gave None for a zero numerator too).  Everything downstream then behaves the
same on both versions without being traced.  Writing needs nothing: 19's
setters still take a Fraction, and copying one stream's attribute straight
to another works on both.
"""

from fractions import Fraction


def q(value):
    """A rational as PyAV 18 gave it: Fraction, or None when unset."""
    if value is None:
        return None
    try:
        num, den = value.numerator, value.denominator
    except AttributeError:
        return value                      # not a rational: leave it alone
    if not num or not den:
        return None
    if isinstance(value, Fraction):
        return value
    return Fraction(num, den)
