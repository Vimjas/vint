import re


OptionalScopeSymbolTable = {
    'g:': True,
    'l:': True,
    'v:': True,
}
optional_scope_prefix_pattern = re.compile(r'^[glv]:')


def remove_optional_scope_prefix(identifier_value): # type: (str) -> str
    # Keep scope prefix if the identifier is a symbol table such as "a:" or "g:".
    # Because it is not optional.
    if OptionalScopeSymbolTable.get(identifier_value, False):
        return identifier_value

    return re.sub(optional_scope_prefix_pattern, '', identifier_value)
