#!/usr/bin/env python3
import csv
import json
import sys
from collections import namedtuple
from os import makedirs
from pathlib import Path
from random import shuffle

import appdirs
import click
import requests

from .html2csv import html2csv


CSV_PATH = Path(appdirs.user_data_dir('completionator', 'steveasleep')) / 'games.csv'
SETTINGS_PATH = Path(appdirs.user_data_dir('completionator', 'steveasleep')) / 'settings.json'
makedirs(str(CSV_PATH.parent), exist_ok=True)


def get_settings(change_user=False):
    if change_user or not SETTINGS_PATH.exists():
        user_id = click.prompt("What's your user ID?", type=int)
        settings = {'user_id': user_id}
        with SETTINGS_PATH.open('w') as f:
            json.dump(settings, f)
        return settings
    else:
        with SETTINGS_PATH.open('r') as f:
            return json.load(f)


def update_csv(user_id):
    r = requests.get(
        'http://completionator.com/Collection/ExportToExcel/{}?keyword=&isHidden=false&shouldBreakOutCompilationGames=true&sortColumn=GameName&sortDirection=ASC'.format(user_id))
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


@click.command()
@click.option('--change-user', default=False, is_flag=True)
@click.option('--update', default=False, is_flag=True)
@click.option('--active', default=False, is_flag=True)
@click.option('--todo', default=False, is_flag=True)
@click.option('--fmt', default='name', type=click.Choice(['name', 'repr', 'csv']))
@click.option('--random/--no-random', default=False)
@click.option('--limit', default=0, type=int)
def cli(change_user, update, active, todo, fmt, random, limit):
    """
    Simple and sane interface to your Completionator collection.

    Made for one purpose: to list games in different states of progress,
    sometimes randomly.
    """

    settings = get_settings(change_user=change_user)

    if update or not CSV_PATH.exists():
        update_csv(user_id=settings['user_id'])

    headings, games = get_games()
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
