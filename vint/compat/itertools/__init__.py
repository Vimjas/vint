try:
    # 3.0 and later
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest
