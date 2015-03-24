from __future__ import unicode_literals
import re


__evaluate_regex = re.compile('`(.*?)`')


def JsonSub(value, data):
    '''
    Expand jsonpaths variables in the given value.

    :param unicode value:
        A text containing jsonpath expression scaped with "`".

    :param object data:
        A JSON compatible python object (dicts, lists, strings, ints, etc).

    :returns unicode:
        Returns the given text with all escaped expressions evaluated based on the given data.
    '''
    def Evaluator(jsonpath_expr, data):
        from jsonpath_rw import parse
        jsonpath_expr = parse(jsonpath_expr)
        matches = jsonpath_expr.find(data)
        return '|'.join([unicode(i.value) for i in matches])

    def Replacer(matchobj):
        return Evaluator(matchobj.group(1), data)

    def Sub(s):
        if s is None:
            return None
        return __evaluate_regex.sub(Replacer, s)

    assert not isinstance(data, unicode), "Expecting a python structure not a json string."

    if type(value) == list:
        return map(Sub, value)
    elif type(value) == tuple:
        return tuple(map(Sub, value))
    else:
        return __evaluate_regex.sub(Replacer, value)


def Remapping(mapping, data):
    '''
    Maps a new value based on existing values on data.

    Expects two special entries in mapping dicitionary:
        __key: Defines how to build the key from the data. Uses JsonSub.
        __default: Defines the default return value for unmatched keys.

    :param dict mapping:
        Maps combinations of values from data to new values.

    :param object data:
        Json compatible python structure.

    :return unicode:
        Returns the matching mapped value found on mapping or the default one
        (mapping['__default'])
    '''
    assert isinstance(mapping, dict)
    assert '__key' in mapping, "Missing key definition entry: '__key'"
    assert '__default' in mapping, "Missing default value entry: '__default'"
    key = JsonSub(mapping['__key'], data)
    value = mapping.get(key, mapping['__default'])
    return JsonSub(value, data)
