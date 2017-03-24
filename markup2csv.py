#!/usr/bin/env python3
import csv
import sys
from html.parser import HTMLParser


writer = csv.writer(sys.stdout)


class CompletionatorHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_row = []
        self._current_row_i = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self._current_row = []
        elif tag == 'td' or tag == 'th':
            self._current_row.append('')

    def handle_endtag(self, tag):
        if tag == 'tr':
            writer.writerow(self._current_row[:6])

    def handle_data(self, data):
        self._current_row[len(self._current_row) - 1] = data


parser = CompletionatorHTMLParser()
with open(sys.argv[1], 'r') as f:
    parser.feed(f.read())
