import csv

from django.conf import settings
from django.http import HttpResponse

DELIMITER = getattr(settings, 'REPORT_DELIMITER', ';')
QUOTECHAR = getattr(settings, 'REPORT_QUOTECHAR', '"')
QUOTING   = getattr(settings, 'REPORT_QUOTING', csv.QUOTE_ALL)


def serve_csv(request):
    if hasattr(request, 'csv_fields') and hasattr(request, 'object_list'):
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % getattr(request, 'csv_filename', 'Untitled.csv')

        writer = csv.writer(response, delimiter=DELIMITER, quotechar=QUOTECHAR, quoting=QUOTING)

        if hasattr(request, 'csv_header'):
            writer.writerow(request.csv_header)

        for obj in request.object_list:
            row = []
            for f in request.csv_fields:
                attr = getattr(obj, f)
                if hasattr(attr, '__call__'):
                    attr = attr()
                row.append(unicode(attr).encode("utf-8"))
            writer.writerow(row)

    return response

