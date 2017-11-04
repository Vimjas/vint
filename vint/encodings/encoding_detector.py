import chardet


class EncodingDetector(object):
    @classmethod
    def _detect_encoding_by_chardet(cls, bytes_seq, file_path):
        # type: (bytes, str) -> str
        is_empty = len(bytes_seq) == 0

        if is_empty:
            return "ascii"

        encoding_hint = chardet.detect(bytes_seq)
        encoding = encoding_hint['encoding']

        if not encoding:
            # Falsey means we cannot detect the encoding of the file.
            raise EncodingDetectionError(file_path)



class EncodingDetectionError(Exception):
    def __init__(self, file_path):
        # type: (str) -> EncodingDetectionError
        self.file_path = file_path


    def __str__(self):
        # type: () -> str
        return 'Cannot detect encoding (binary file?): {file_path}'.format(
            file_path=str(self.file_path))
