# swl-assets — the asset store for the Iron Squadron work on the SWL TTS mod

Every file Tabletop Simulator downloads at runtime for our additions to the
Star Wars Legion mod lives here, and nowhere else. This repository holds no
code and takes no pull requests against its contents: its only job is to be
a stable address.

Serve a file from the `main` branch, raw:

```
https://raw.githubusercontent.com/ironsquadronfr-hub/swl-assets/main/assets/<file>
```

## The three rules

**1. Never delete a file.** A URL that has ever been live is referenced by
saves we cannot see — a playtester's table from three weeks ago, someone's
copy of the mod. Ninety megabytes cost nothing; a save that no longer loads
costs a player. Files that nothing in the current code references stay
anyway, and the manifest marks them.

**2. Never rename or overwrite a file.** TTS caches by URL: an asset changed
in place reaches everyone who already has it as the *old* file, forever,
because their cache never asks again. A new version is a **new name** —
`projector_100mm_isq_v6.unity3d` becomes `..._v7`, never `v6` with different
bytes. `MANIFEST.csv` records the sha256 of every file precisely so this
rule can be checked rather than trusted.

**3. Every file is listed in `MANIFEST.csv`.** Name, sha256, size, the batch
it came from, and where it came from originally. A file on disk that is not
in the manifest, or a manifest line with no file, is a bug.

## The one folder with other rules: `assets/veil-backdrops/`

The pictures behind the loading veil, shown in turn, one per load. The mod
lists this folder through the GitHub API, so the folder IS the list: drop a
picture in to add it to the rotation, delete it to take it out. No code
change, no manifest line.

- **Deleting is allowed here**, and only here: a picture leaves the rotation
  when its contract or its season ends. A save still pointing at it shows
  the plain dark veil once, then moves on to the next picture.
- **Never replace a picture under the same name.** TTS caches by URL, so a
  player who has seen the old one would keep seeing it for good. A new
  picture is a new name.
- 16:9, 1920x1080, JPG or PNG, no text and no dark band of its own: the
  band, the logo and the shortcut sheet are drawn on top.

## What is in here

| batch | files | what it is |
|---|---:|---|
| `isq-metal-rebuilds` | 82 | Unity bundles rebuilt for Metal, the Mac rendering fix |
| `isq-overlay-assets` | 89 | range and cohesion overlays, projectors, silhouettes |
| `isq-token-assets` | 16 | the V2 tokens, including the dual-platform smoke volume |
| `isq-map-assets` | 3 | the Imperial Checkpoint marble, recovered from the Wayback Machine, and the POI guide projector (v1, v2) |
| `featured-maps` | 64 | Featured Map assets rescued off fragile third-party hosts, and two that died on Steam |

The `featured-maps` batch deserves a word. The ten Featured Maps pull 258
assets, and 196 of those sit on Steam's own CDN — the same host the whole
mod already depends on, so re-hosting them would buy nothing and cost 58 MB.
The other 62 sat on personal imgur accounts, one author's Dropbox,
anonymous gists, a pastebin and a texture site. Those are the ones here.
Two more joined later: the mesh and texture of Geonosis's "Destroyed
Advanced Dwarf Spider Droid", which did die on Steam. No copy survived
anywhere public; these are the original bytes, recovered from a player's TTS
cache. Their original addresses are in the manifest's `origine` column.

## Checking the store is alive

```
python3 tools/audit_urls.py           # every URL answers (ranged GET, fast)
python3 tools/audit_urls.py --deep    # ...and the bytes still hash right
```

The fast pass is what belongs on a schedule. HEAD requests lie on some CDNs
— they answer 200 for files that are gone — so the audit always asks for a
byte range instead.

## Why a repository of its own

These files used to live on `mod/data/` of the `isq-qol` branch of our fork
of the mod: a feature branch doing double duty as a CDN. That works right
up until someone renames the branch, force-pushes it, or deletes it after a
merge — and then the mod stops installing for everyone. It has happened
before to this mod, when the host the original authors used went dark and
took 803 assets with it. Those old paths are still live and will stay live;
nothing new goes there.
