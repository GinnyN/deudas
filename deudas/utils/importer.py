"""
.. module:: utils.importer
"""

from itertools import starmap, dropwhile

import xlrd
from xlutils.view import SheetView


def read_file(f, ncols=1):
    """
    Reads a xls file and returns the contents of the first sheet. The
    first row is discarded as it's assumed to contain headers.
    """
    wb = xlrd.open_workbook(file_contents=f.read())
    sheet = wb.sheet_by_index(0)
    if sheet.ncols == 0: raise ValueError("empty sheet")
    if sheet.ncols < ncols: raise ValueError("insufficient columns")
    view = SheetView(wb, sheet)
    return starmap(lambda index, row: (index, list(row)),
                   dropwhile(lambda pair: pair[0] == 0, enumerate(view)))
