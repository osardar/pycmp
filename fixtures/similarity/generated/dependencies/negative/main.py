def visit(name, graph, seen, output):
    if name in seen:
        return
    seen.add(name)
    for child in graph.get(name, []):
        visit(child, graph, seen, output)
    output.append(name)

def _original_run(payload):
    output = []
    visit(payload['root'], payload['graph'], set(), output)
    return output

def run(payload):
    return [_original_run(payload), 'changed']
