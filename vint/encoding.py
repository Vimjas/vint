import chardet


class EncodingDetectionError(Exception):
    def __init__(self, file_path):
        self.file_path = file_path


    def __str__(self):
        return 'Cannot detect encoding (binary file?): {file_path}'.format(
            file_path=str(self.file_path))


def guess_encoding(bytes_seq, opt_file_path='unknown'):
    encoding_hint = chardet.detect(bytes_seq)

    encoding = encoding_hint['encoding']
    if not encoding:
        # Falsey means we cannot detect the encoding of the file.
        raise EncodingDetectionError(opt_file_path)

    return encoding
