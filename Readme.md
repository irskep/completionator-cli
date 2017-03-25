# Completionator CLI

Command line interface for [Completionator](http://completionator.com/).

To feel better about your life, see [the author's profile](http://completionator.com/Collection/Stats/13863).

```
Usage: __main__.py [OPTIONS]

  Simple and sane interface to your Completionator collection.

  Made for one purpose: to list games in different states of progress,
  sometimes randomly.

  Examples:

      # show all games you're currently playing     python -m completionator
      --active

      # show 2 random unplayed games     python -m complationator --todo

Options:
  --change-user           Prompt to re-enter user ID
  --update                Update data from server
  --active                Show 'now playing'
  --todo                  Show incomplete
  --fmt [name|repr|csv]   Output format
  --random / --no-random  Shuffle output
  --limit INTEGER         Truncate results (0=don't truncate; default)
  --help                  Show this message and exit.
```