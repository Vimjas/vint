from typing import Dict, Any


class AbstractASTPlugin(object):
    """ An abstract class for AST plugins. AST plugins can add attributes to
    the AST. But for maintainability reason, overwriting or deleting any
    attribute is prohibited.
    """

    def process(self, ast):
        # type: (Dict[str, Any]) -> Dict[str, Any]
        return ast
