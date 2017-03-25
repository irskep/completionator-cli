#!/usr/bin/env python3
import csv
from html.parser import HTMLParser


class CompletionatorHTMLParser(HTMLParser):
    """Interpret Completionator's silly "excel" format (i.e. HTML table)"""

    def __init__(self, writer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.writer = writer
        self._current_row = []
        self._current_row_i = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self._current_row = []
        elif tag == 'td' or tag == 'th':
            self._current_row.append('')

    def handle_endtag(self, tag):
        if tag == 'tr':
            # remaining columns tend to be empty
            self.writer.writerow(self._current_row[:6])

    def handle_data(self, data):
        self._current_row[len(self._current_row) - 1] = data


def html2csv(s, out_file):
    writer = csv.writer(out_file)
    parser = CompletionatorHTMLParser(writer)
    parser.feed(s)
