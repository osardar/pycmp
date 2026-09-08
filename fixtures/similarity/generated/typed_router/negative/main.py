type Batch[T] = list[T]

def first[T](values: Batch[T]) -> T:
    return values[0]

def _original_run(payload):
    output = []
    errors = []
    for message in payload['messages']:
        match message:
            case {'kind': 'value', 'items': items} if items:
                output.append(first(items))
            case _:
                errors.append(ValueError('invalid message'))
    if errors:
        try:
            raise ExceptionGroup('messages', errors)
        except* ValueError as group:
            output.append(len(group.exceptions))
    return output

def run(payload):
    return [_original_run(payload), 'changed']
