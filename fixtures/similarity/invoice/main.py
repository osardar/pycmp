from pricing import discounted

def run(payload):
    lines = [discounted(row[0] * row[1], payload["discount"]) for row in payload["items"]]
    return {"total": sum(lines), "count": len(lines)}
