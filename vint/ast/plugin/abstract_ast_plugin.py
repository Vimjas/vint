class AbstractASTPlugin(object):
    """ An abstract class for AST plugins. AST plugins can add attributes to
    the AST. But for maintainability reason, overwriting or deleting any
    attribute is prohibited.
    """

    def process(self, ast):
        return ast
