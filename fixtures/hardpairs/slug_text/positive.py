def run(p):
    trimmed = p.strip()
    lowered = trimmed.lower()
    return '-'.join(lowered.split(' '))
