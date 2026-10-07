from fpl import money


def build(run):
    d = run["data"]
    return {"bank": money.price(d["money"]["bank"]),
            "free_transfers": str(d["money"]["free_transfers"]),
            "formation": d["lineup"]["formation"]}
