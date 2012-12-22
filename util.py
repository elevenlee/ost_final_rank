def parse_string(string, split=','):
    """Returns the result list of parse specified string 

    :param string the specified string to be parsed
    :param split the specified split character. The default value
                 is ',' (comma).
    :returns the result list of parse specified string
    """
    string = string[1:-1]
    str_list = string.split(split)
    return [result.strip(' ')[2:-1] for result in str_list]

