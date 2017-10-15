#!/usr/bin/env python3
import csv
import json
import math
import sys
from collections import namedtuple
from os import makedirs
from pathlib import Path
from random import shuffle

import appdirs
import click
import requests
from terminaltables import SingleTable

from .html2csv import html2csv


CSV_PATH = Path(
    appdirs.user_data_dir('completionator', 'steveasleep')) / 'games.csv'
SETTINGS_PATH = Path(
    appdirs.user_data_dir('completionator', 'steveasleep')) / 'settings.json'
makedirs(str(CSV_PATH.parent), exist_ok=True)


def get_settings(change_user=False):
    if change_user or not SETTINGS_PATH.exists():
        user_id = click.prompt(
            "What's your user ID? (Go to 'My Profile', copy the number at the"
            " end of the URL)",
            type=int)
        settings = {'user_id': user_id}
        with SETTINGS_PATH.open('w') as f:
            json.dump(settings, f)
        return settings
    else:
        with SETTINGS_PATH.open('r') as f:
            return json.load(f)


def update_csv(user_id):
    click.echo(
        click.style('Requesting data from server...', fg='blue'), err=True)
    r = requests.get(
        ('http://completionator.com/Collection/ExportToExcel/{}'
         '?keyword=&isHidden=false&shouldBreakOutCompilationGames=true'
         '&sortColumn=GameName&sortDirection=ASC').format(user_id))
    with CSV_PATH.open('w') as f:
        html2csv(r.text, f)


def get_games():
    with CSV_PATH.open('r') as f:
        reader = csv.reader(f)
        headings = next(reader)
        fields = [
            field.lower().replace(' ', '_')
            for field in headings
        ]
        Game = namedtuple('Game', fields)
        return headings, [Game(*columns) for columns in reader]


def _get_stats(games):
    num_done = len(
        [g for g in games
         if g.progress_status in ('Finished', 'Completionated')])
    num_excluded = len(
        [g for g in games if g.progress_status in ('Never Playing',)])
    num_incomplete = len(
        [g for g in games if g.progress_status in ('Incomplete',)])
    num_active = len([g for g in games if g.now_playing == 'Yes'])

    fraction_complete = num_done / (len(games) - num_excluded)
    percent_complete = "{}%".format(math.floor(fraction_complete * 100))

    return {
        'num_done': num_done,
        'num_excluded': num_excluded,
        'num_incomplete': num_incomplete,
        'num_active': num_active,
        'percent_complete': percent_complete,
        'num_all': len(games),
    }


def _get_table_data(games):
    stats = _get_stats(games)
    return [
        ['Total games', stats['num_all']],
        ['Finished', stats['num_done']],
        ['Excluded', stats['num_excluded']],
        ['Incomplete', stats['num_incomplete']],
        ['Active', stats['num_active']],
        ['% complete', stats['percent_complete']],
    ]


def print_stats(games):
    table = SingleTable(_get_table_data(games), title='Game stats')
    table.inner_heading_row_border = False
    click.echo(table.table)


def print_html(games):
    table_data = _get_table_data(games)
    print("""
<html>
    <head>
        <title>Games</title>
        <link href="style.css" rel="stylesheet">
    </head>
    <body>
    """.strip())

    print('<h1>Stats</h1>')

    print('<table class="completionator-stats">')
    for label, value in table_data:
        print('<tr><td class="label">{label}</td><td class="value">{value}</td></tr>'.format(label=label, value=value))
    print('</table>')

    print('<h1>Games</h1>')

    print('<h2>Active</h2>')
    print('<ul class="completionator-games-active">')
    for game in games:
        if game.now_playing == 'Yes':
            print('<li>{}</li>'.format(game.name))
    print('</ul>')

    print('<h2>Incomplete and inactive</h2>')
    print('<ul class="completionator-games-incomplete">')
    for game in games:
        if game.now_playing != 'Yes' and game.progress_status == 'Incomplete':
            print('<li>{}</li>'.format(game.name))
    print('</ul>')

    print('<h2>Complete</h2>')
    print('<ul class="completionator-games-complete">')
    for game in games:
        if game.progress_status in ('Finished', 'Completionated'):
            print('<li>{}</li>'.format(game.name))
    print('</ul>')

    print("""
    </body>
</html>
    """.strip())


@click.command()
@click.option('--change-user', default=False, is_flag=True, help="Prompt to re-enter user ID")
@click.option('--update', default=False, is_flag=True, help="Update data from server")
@click.option('--active', default=False, is_flag=True, help="Show 'now playing'")
@click.option('--todo', default=False, is_flag=True, help="Show incomplete")
@click.option('--fmt', default='name', type=click.Choice(['name', 'repr', 'csv']), help="Output format")
@click.option('--random/--no-random', default=False, help="Shuffle output")
@click.option('--limit', default=0, type=int, help="Truncate results (0=don't truncate; default)")
@click.option('--stats', default=False, is_flag=True, help="Print some stats to stderr")
@click.option('--html', default=False, is_flag=True, help="Print HTML representation of everything")
def cli(change_user, update, active, todo, fmt, random, limit, stats, html):
    """
    Simple and sane interface to your Completionator collection.

    Made for two purposes: to list games in different states of progress,
    sometimes randomly; and to show basic statistics.

    Examples:

        \b
        # show all games you're currently playing
        > python -m completionator --active

        \b
        # show 2 random unplayed games
        > python -m completionator --todo

        \b
        # show stats
        > python -m completionator --stats
        ┌Game stats───┬─────┐
        │ Total games │ 475 │
        │ Finished    │ 135 │
        │ Excluded    │ 66  │
        │ Incomplete  │ 259 │
        │ Active      │ 37  │
        │ % complete  │ 33% │
        └─────────────┴─────┘
    """

    settings = get_settings(change_user=change_user)

    if update or not CSV_PATH.exists():
        update_csv(user_id=settings['user_id'])

    headings, games = get_games()

    if html:
        print_html(games)

    if stats:
        print_stats(games)

    filtered_games = [
        g for g in games if (
            active and g.now_playing == 'Yes' or
            todo and g.progress_status == 'Incomplete'
        )
    ]
    if random:
        shuffle(filtered_games)
    if limit:
        filtered_games = filtered_games[:limit]

    csv_writer = None
    if fmt == 'csv':
        csv_writer = csv.writer(sys.stdout)
        csv_writer.writerow(headings)

    for game in filtered_games:
        if fmt == 'name':
            click.echo(game.name)
        elif fmt == 'repr':
            click.echo(repr(game))
        elif fmt == 'csv':
            csv_writer.writerow(game)


if __name__ == '__main__':
    cli()
