"""Provider-neutral token arithmetic after explicit field normalization."""


def token_total(input_tokens, output_tokens, thought_tokens, cached_tokens,
                thought_in_output=False):
    values = (input_tokens, output_tokens, thought_tokens, cached_tokens)
    if any(value is not None and (type(value) is not int or not 0 <= value <= 10**12) for value in values):
        raise ValueError("invalid token count")
    if type(thought_in_output) is not bool:
        raise ValueError("reasoning inclusion must be explicit")
    if cached_tokens is not None and input_tokens is not None and cached_tokens > input_tokens:
        raise ValueError("cached tokens must be normalized as an input subset")
    if thought_in_output and thought_tokens is not None and output_tokens is not None and thought_tokens > output_tokens:
        raise ValueError("reasoning tokens exceed inclusive output")
    if input_tokens is None or output_tokens is None or (not thought_in_output and thought_tokens is None):
        return None
    return input_tokens + output_tokens + (0 if thought_in_output else thought_tokens)
