import tempfile


def tmpfile(max_size=131072, folder=None, pre="tmp_", ext="pdf"):
    if folder is None:
        folder = tempfile.gettempdir()
    try:
        folder = tempfile.SpooledTemporaryFile(max_size=max_size, dir=folder, prefix=pre, suffix='.%s' * ext)
    except:
        print "Error: can't created temporary file"

    return file
