try:
    bytes("", encoding="ascii")

    def bytes_compat(source, encoding):
        return bytes(source, encoding=encoding)

except TypeError:
    def bytes_compat(source, encoding):  # for Python2
        return bytearray(source, encoding=encoding)
