from debug import DEBUG

PRE = "<|fim_prefix|>"
MID = "<|fim_middle|>"
SUF = "<|fim_suffix|>"
EOT = "<|endoftext|>"
START_MARKS = ["def "]
END_MARKS = ["@", "class ", "def "]

def _split(prompt: str) -> tuple[str, str, str]:
    _, rest = prompt.split(PRE)
    prefix, rest = rest.split(SUF)
    suffix, middle = rest.split(MID)
    return (prefix, middle, suffix)
def _construct_prompt(prefix: str, middle: str, suffix: str) -> str:
    return PRE + prefix + SUF + suffix + MID + middle
def _construct_function_prompt(prefix: str, f_prefix: str, middle: str, f_suffix: str, suffix: str) -> str:
    return PRE + prefix + SUF + suffix + PRE + f_prefix + SUF + f_suffix + MID + middle
def _split_line(total: str, line_number: int) -> tuple[str, str, str]:
    lines = total.splitlines()
    previous_lines = lines[:line_number]
    current_line = lines[line_number]
    suffix_lines = lines[line_number+1:]
    return "\n".join(previous_lines) + "\n", current_line, "\n".join(suffix_lines) + "\n"
def _detect_function_prefix(prefix: str) -> int | None:
    lines = prefix.splitlines()
    for i in range(len(lines)-1, -1, -1):
        line = lines[i]
        if any([line.lstrip().startswith(mark) for mark in START_MARKS]):
            return i
    return None
def _detect_stop_suffix(suffix: str) -> int:
    lines = suffix.splitlines()
    for i in range(len(lines)):
        line = lines[i]
        if any([line.lstrip().startswith(mark) for mark in END_MARKS]):
            return i
    return len(lines)
def function_cache(prompt: str) -> str:
    prompt = prompt.replace("\r\n", "\n")
    if DEBUG:
        with open("log/original.py", 'w', encoding='utf-8') as file:
            file.write(prompt)
    preffix, middle, suffix = _split(prompt)
    
    total = preffix + middle + suffix
    lines = total.splitlines()
    position = len(preffix)
    function_line = _detect_function_prefix(preffix) or 0
    end_line = _detect_stop_suffix(suffix) + len(preffix.splitlines()) - 1
    
    previous_lines = lines[:function_line]
    after_lines = lines[end_line:]
    if len(previous_lines) == 0:
        previous = ""
    else:
        previous = "\n".join(previous_lines) + "\n"
    if len(after_lines) == 0:
        after = ""
    else:
        after = "\n".join(after_lines) + "\n"
    previous_in_function = total[len(previous):position]
    after_in_function = total[position:len(total)-len(after)]

    result = _construct_function_prompt(
        previous,
        previous_in_function,
        "",
        after_in_function,
        after
    )
    if DEBUG:
        with open("log/cache.py", 'w', encoding='utf-8') as file:
            file.write(result)
    return result
def line_cache(prompt: str) -> str:
    prompt = prompt.replace("\r\n", "\n")
    if DEBUG:
        with open("log/original.py", 'w', encoding='utf-8') as file:
            file.write(prompt)
    preffix, middle, suffix = _split(prompt)
    
    total = preffix + middle + suffix
    line_number = len(preffix.splitlines()) - 1
    preffix, middle, suffix = _split_line(total, line_number)
    
    result = _construct_prompt(preffix, middle, suffix)
    if DEBUG:
        with open("log/cache.py", 'w', encoding='utf-8') as file:
            file.write(result)
    return result