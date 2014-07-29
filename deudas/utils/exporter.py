# -*- coding: utf-8 -*-
"""
.. module:: utils.exporter
   :synopsis: Provides generic file-exporting functions.
"""

import xlwt

from django.http import HttpResponse


# Style constants

#: Style to be applied to date and datetime columns.
DATESTYLE = xlwt.easyxf("", "DD/MM/YYYY")

#: Default style for text cells.
DEFAULTSTYLE = xlwt.easyxf("align: wrap on")

#: Style to be applied to headers.
_HEADERSTYLE = xlwt.easyxf("font: bold on; "
                           "align: wrap on, vert center, horiz center")

#: Unit of with for columns.
_COLUMN_WIDTH = 1344


def make_xls(target, data, sheetname=None, headers=(), styles=None):
    book = xlwt.Workbook()
    sheet = book.add_sheet(sheetname or u"Exportación de datos")
    for c, h in enumerate(headers):
        w = 4
        if isinstance(h, tuple):
            h, w = h
        w = w * _COLUMN_WIDTH
        sheet.write(0, c, h, _HEADERSTYLE)
        sheet.col(c).width = w
    sheet.row(0).height = 0x0300

    write = (lambda r, c, cell: sheet.write(r, c, cell, styles[c]) \
                 if styles[c] is not None else \
                 sheet.write(r, c, cell, DEFAULTSTYLE)) \
                 if styles else \
                 (lambda r, c, cell: sheet.write(r, c, cell, DEFAULTSTYLE))

    for r, row in enumerate(data, start=1):
        for c, cell in enumerate(row): write(r, c, cell)
    book.save(target)


def xls_response(filename, data, sheetname=None, headers=(), styles=None):
    response = HttpResponse()
    response['Content-Disposition'] = u"attachment; filename={0}.xls".\
        format(filename)
    response['Content-Type'] = "application/vnd.ms-excel"
    make_xls(response, data, sheetname=sheetname, headers=headers, styles=styles)
    return response
