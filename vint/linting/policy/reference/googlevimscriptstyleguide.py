SectionNames = {
    # Portability
    'STRINGS': 'Strings',
    'MATCHING': 'Matching',
    'REGULAR': 'Regular',
    'EXPRESSIONS': 'Expressions',
    'DANGEROUS': 'Dangerous',
    'COMMANDS': 'Commands',
    'FRAGILE': 'Fragile',
    'CATCHING': 'Catching',
    'EXCEPTIONS': 'Exceptions',

    # General Guidelines
    'MESSAGING': 'Messaging',
    'TYPE': 'Type',
    'CHECKING': 'checking',
    'PYTHON': 'Python',
    'OTHER': 'Other',
    'LANGUAGES': 'Languages',
    'BOILERPLATE': 'Boilerplate',
    'PLUGIN': 'Plugin',
    'LAYOUT': 'Layout',
    'FUNCTIONS': 'Functions',
    'AUTOCOMMANDS': 'Autocommands',
    'MAPPINGS': 'Mappings',
    'SETTINGS': 'Settings',

    # Style
    'WHITESPACE': 'Whitespace',
    'NAMING': 'Naming',
}


def get_reference_source(section):
    return 'Google VimScript Style Guide ({section_name})'.format(
        section_name=SectionNames[section])
