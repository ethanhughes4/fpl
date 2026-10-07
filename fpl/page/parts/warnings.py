from fpl.sections import warnings


def build(run):
    w = run["data"]["warnings"]
    return {"rows": [{"name": x["name"], "chance": f"{x['chance']}%", "news": warnings.news(x)} for x in w],
            "empty": None if w else warnings.render(w)[0]}  # "Warnings: none" (D295)
