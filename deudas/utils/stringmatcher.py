# -*- coding: utf-8 -*-
"""
.. module:: utils.stringmatcher
   :synopsis: Provides facilities to match strings.
"""

import operator


def striptildes(s):
    return u"".join(
        {u"Á": "A",
         u"É": "E",
         u"Í": "I",
         u"Ó": "O",
         u"Ú": "U",
         u"á": "a",
         u"é": "e",
         u"í": "i",
         u"ó": "o",
         u"ú": "u"}.get(c, c)
        for c in s)


prepositions = set(["de", "para", "a", "por", "con",
                    "DE", "PARA", "A", "POR", "CON"])

def stripprepositions(s):
    words = s.split()
    return u" ".join(word for word in words
                     if word not in prepositions)


def distance(s1, s2):
    """
    Levenshtein distance. Source:
    http://en.wikibooks.org/wiki/Algorithm_implementation/Strings/Levenshtein_distance#Python
    """
    if len(s1) < len(s2):
        return distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
 
    return previous_row[-1]


def similar(s1, s2):
    return distance(striptildes(s1.upper()),
                    striptildes(s2.upper())) <= min(len(s1), len(s2)) // 3


def mapmatch(fn, s, options):
    for option in options:
        if similar(s, fn(option)): return option
