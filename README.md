# find-life

Look up the taxonomy of any organism by scientific or common name directly from your terminal. Pulls data from [find-life.org](https://find-life.org), which sources taxonomy from find-life-database (an actively maintained fork of [ITIS](https://www.itis.gov/)), fossil records from the [Paleobiology Database](https://paleobiodb.org/), and summaries from [Wikipedia](https://www.wikipedia.org/).

## Install

```sh
pip install find-life
# or
uv tool install find-life
```

If you don't have a Python environment configured, I recommend installing [uv](https://docs.astral.sh/uv/) first:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then run `uv tool install find-life`.

## Usage

```sh
find-life search <name> [OPTIONS]
```

**Options:**

| Flag | Description |
|---|---|
| `--scientific` | Search scientific names only |
| `--common` | Search vernacular names only |
| `-f`, `--format` | Output format: `text` (default), `table`, or `json` |

**Examples:**

```sh
find-life search penguin
find-life search "Sphenisciformes" --scientific
find-life search penguin --format json
find-life search penguin --format table
```

**Output (`text` format):**

```
Taxonomy:
Chordata  (Phylum)
  └─ Vertebrata  (Subphylum)
    └─ ...
      └─ ▶  Sphenisciformes  (Order)
         └─ Spheniscidae  (Family)

First appeared: 66 – 59.24 Ma

Wikipedia: Penguins are a group of flightless semi-aquatic sea birds...
Source:    https://en.wikipedia.org/wiki/Penguin
```

## Configuration

Authenticates with find-life.org using a token provisioned automatically, stored in `~/.find-life/config.json`. Run `find-life init` to reset it.

## Website

More awaits at [find-life.org](https://find-life.org), where you can navigate the tree of life interactively. Happy finding!
