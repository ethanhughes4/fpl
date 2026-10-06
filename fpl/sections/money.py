from fpl import money


def build(feed):
    return {"bank": money.bank(feed), "free_transfers": money.free_transfers(feed)}


def render(data):
    return [f"Bank {money.price(data['bank'])} · Free transfers {data['free_transfers']}"]
