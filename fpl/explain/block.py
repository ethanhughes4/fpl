from fpl.explain.parts import brief

PARTS = [brief]


def build(data, feed):
    return "\n".join(line for p in PARTS for line in p.lines(data, feed))
