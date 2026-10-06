from fpl import brief


def lines(data, feed):
    return brief.render(data).split("\n")
