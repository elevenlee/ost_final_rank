def parse_string(string, split=','):
    string = string[1:-1]
    str_list = string.split(split)
    return [result.strip(' ')[2:-1] for result in str_list]

