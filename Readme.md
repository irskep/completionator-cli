# Completionator CLI

Command line interface for [Completionator](http://completionator.com/).

To feel better about your life, see [the author's profile](http://completionator.com/Collection/Stats/13863).

```
Usage: __main__.py [OPTIONS]

  Simple and sane interface to your Completionator collection.

  Made for two purposes: to list games in different states of progress,
  sometimes randomly; and to show basic statistics.

  Examples:

          # show all games you're currently playing
          > python -m completionator --active

          # show 2 random unplayed games
          > python -m completionator --todo

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

Options:
  --change-user           Prompt to re-enter user ID
  --update                Update data from server
  --active                Show 'now playing'
  --todo                  Show incomplete
  --fmt [name|repr|csv]   Output format
  --random / --no-random  Shuffle output
  --limit INTEGER         Truncate results (0=don't truncate; default)
  --stats                 Print some stats to stderr
  --help                  Show this message and exit.
```