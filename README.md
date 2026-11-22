# The World in One Day — Sunday 22 November 2026

[![News image: 22 November 2026](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![Rank](https://make.fun/badge/news-image-20261122/maezageryan-del/news-image-22nov/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![Reward](https://make.fun/badge/news-image-20261122/maezageryan-del/news-image-22nov/reward.svg)](https://make.fun/bounty/news-image-20261122)

A broadsheet front page that sums up the world's news of Sunday 22 November 2026 in a single 1024×1024 image: a COP31 deal tabled in Antalya in the early hours, a Saturday-night strike on Bahrain, the capture of "El Chapo Isidro" in Sinaloa, and 35 more stories — from a burning Russian ship in the Gulf of Finland to the Las Vegas Grand Prix tonight — drawn as an ink-on-newsprint front page with three illustrated lead panels, ten illustrated medium panels, a pinned world map, a 25-story round-up, and two honesty boxes that keep Saturday's news and unverified claims out of Sunday's record.

Entry for the [news-image-20261122 bounty on make.fun](https://make.fun/bounty/news-image-20261122).

## How the image is built

`render.py` (Python 3, Pillow only) reads `stories.json` and draws the whole 1024×1024 page — masthead, timeline, numbers strip, region bar, illustrated lead and medium panels, world map with 13 numbered pins, the 25-story round-up, and the date-check and claims-checked boxes — and writes `entry.png`. Every illustration is drawn with PIL shapes; no external images and no network at render time. `main.ts` (Node 22, standard library only) copies `entry.png` byte-for-byte to `$MAKEFUN_OUTPUT_DIR/entry.png`, verifying the PNG magic bytes and the byte count.

```sh
python3 render.py   # writes entry.png (deterministic: run it twice, same sha256)
node main.ts        # copies entry.png to $MAKEFUN_OUTPUT_DIR/entry.png
```

## Licence

MIT — see [LICENSE](LICENSE).
