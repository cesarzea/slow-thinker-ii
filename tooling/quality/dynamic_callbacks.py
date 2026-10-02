"""Checked standard-library callback references for Vulture's dynamic-dispatch analysis.

HTMLParser.feed calls these overridden methods by framework dispatch. Their
signatures are checked with typing.override; the public tariff parser tests
exercise both callbacks. Explicit references follow Vulture's documented method
for false positives, without excluding source files or changing confidence.
"""

from html.parser import HTMLParser

HTML_PARSER_CALLBACKS = (HTMLParser.handle_starttag, HTMLParser.handle_endtag)
