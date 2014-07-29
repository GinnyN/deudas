from django import template

register = template.Library()

@register.simple_tag
def pagenumber(example=None):
    if example:
        return u'<pdf:pagenumber example="%s" />' % example
    else:
        return u'<pdf:pagenumber />'

@register.simple_tag
def nexttemplate(name=None):
    if name:
        return u'<pdf:nexttemplate name="%s" />' % name
    else:
        return u'<pdf:nexttemplate />'

@register.simple_tag
def nextpage(name=None):
    if name:
        return u'<pdf:nextpage name="%s" />' % name
    else:
        return u'<pdf:nextpage />'


@register.simple_tag
def nextframe():
    return u'<pdf:nextframe />'

@register.simple_tag
def spacer(height=None):
    if height:
        return u'<pdf:spacer height="%s" />' % height
    else:
        return u'<pdf:spacer />'

@register.simple_tag
def toc():
    return u'<pdf:toc />'

@register.simple_tag
def fontembed(name, src):
    return u'<pdf:fontembed name="%s" src="%s" />' % (name, src)

@register.simple_tag
def barcode(value, align="center"):
    return u'<pdf:barcode value="%s" align="%s" />' % (value, align)
