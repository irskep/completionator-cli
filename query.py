#!/usr/bin/env python3
import csv
from collections import namedtuple
from random import choice

import click


def get_games():
    games = None
    with open('games.csv', 'r') as f:
        reader = csv.reader(f)
        fields = [
            field.lower().replace(' ', '_')
            for field in next(reader)
        ]
        Game = namedtuple('Game', fields)
        return [Game(*columns) for columns in reader]


@click.command()
@click.option('--active', default=False, is_flag=True)
@click.option('--todo', default=False, is_flag=True)
@click.option('--print-repr', default=False, is_flag=True)
@click.option('--random/--no-random', default=False)
def cli(active, todo, print_repr, random):
    games = get_games()

    filtered_games = []
    if active:
        filtered_games.extend([g for g in games if g.now_playing == 'Yes'])
    if todo:
        filtered_games.extend([g for g in games if g.progress_status == 'Incomplete'])
    if random:
        filtered_games = [choice(filtered_games)]
    for game in filtered_games:
        if print_repr:
            click.echo(repr(game))
        else:
            click.echo(game.name)


if __name__ == '__main__':
    cli()
