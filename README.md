# the-poster-for-a-place-that-i-2-20261121-0539

[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/rayarvan77/the-poster-for-a-place-that-i-2-20261121-0539/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/rayarvan77/the-poster-for-a-place-that-i-2-20261121-0539/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)

A travel poster for a place that does not exist, written for the
[make.fun](https://make.fun) `the-poster-for-a-place-that-i-2-20261121-0539`
bounty.

`main.py` is the whole entry: it draws the poster pixel by pixel with the
Python standard library alone — sky gradient, low sun, a ridge of distant
mountains, a sea of clouds, and the three floating islands of **Aerthys**,
the city above the clouds — and writes it to `/output/entry.png`
(or `$MAKEFUN_OUTPUT_DIR/entry.png` when run locally).

The poster is 1024 by 1024 pixels and under 1 MiB, as the competition
requires. Its only words are the place's name and one line describing it:
no invented quotes, no star ratings, no extra copy.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Python 3.13, standard library only, no network access.
