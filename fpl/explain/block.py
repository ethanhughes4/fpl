from fpl.explain.parts import breakdown, brief, close

PARTS = [brief, close, breakdown]


def build(data, feed):
    return "\n".join(line for p in PARTS for line in p.lines(data, feed))
