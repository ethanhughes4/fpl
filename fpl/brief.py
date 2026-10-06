from fpl.sections import header

SECTIONS = [header]


def _name(s):
    return s.__name__.rsplit(".", 1)[-1]


def build(feed):
    return {_name(s): s.build(feed) for s in SECTIONS}


def render(data):
    return "\n".join(line for s in SECTIONS for line in s.render(data[_name(s)]))
