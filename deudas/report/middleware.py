import sys, os, re, StringIO
import ho.pisa as pisa

from django.conf import settings


def fetch_resources(uri, rel):
    """
    Callback to allow pisa/reportlab to retrieve Images,Stylesheets, etc.
    `uri` is the href attribute from the html link element.
    `rel` gives a relative path, but it's not used here.

    """
    path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    print "FETCHING: %s" % path
    return path


class DownloadToPDF():
    """
    Download requested page in PDF format
    """
       
    def process_response(self, request, response):
        if ("pdf" in request.GET 
            and "text" in response['Content-Type'] 
            and response.status_code == 200):
            
            fd  = StringIO.StringIO()
            pdf = pisa.CreatePDF(response.content, fd, None, fetch_resources, 0, None, None)

#           pisa.showLogging()
#           pdf = pisa.pisaDocument(
#               response.content,   # src
#               fd,                 # dest
#               debug=0,
#               path=None,
#               errout=sys.stdout
#               tempdir=None,
#               format = 'pdf',
#               link_callback = fetch_resources,
#               encoding = 'iso-8859-1',
#               default_css=None,
#               xhtml=True,
#               xml_output=fd,
#           )
            
            if not pdf.err:
                response['Content-Type'] = u'%s; %s' % (settings.REPORT_CONF['content_type'], settings.REPORT_CONF['encoding'], )
                response.content = fd.getvalue()
            fd.close()

        return response


