"""
.. module:: utils.forms
   :synopsis: General utilities for form usage.
"""

def first_error_message(form):
    if not hasattr(form, '_errors'): return None
    if not form._errors: return None
    key = form._errors.keys()[0]
    label = form.fields[key].label if key != "__all__" else None
    return u"{0}{1}".format(label + u": " if label else u"", form._errors[key][0])
