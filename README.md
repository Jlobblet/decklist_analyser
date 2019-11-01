# decklist_analyser
decklist_analyser takes Magic: the Gathering decklists in CSV form from
a specific source and uses them to either check for overlapping cards
between lists or group decks based on the cards they contain into
distinct clusters detected algorithmically.
## Installation
Installing decklist_analyser can be tricky thanks to some of the
packages used.
### Simple method
Run `pip install -r requirements.txt` and hope it works
### Involved method (Windows)
Start by installing `numpy`, `pandas` and `regex` with whatever package
manager you prefer.
Next, attempt to install `pycairo`. If this fails, try the wheels
located at https://www.lfd.uci.edu/~gohlke/pythonlibs/.
Then, install `python-igraph`. It's important to do them this way
around - `python-igraph` depends on `pycairo` and if you are manually
downloading the wheels it won't use those, but rather download its own
and fail. The above URL has wheels for `python-igraph`.
Finally, install `louvain`. Again, the above URL has the wheels.
### Involved method (Unix)
Start by installing `numpy`, `pandas` and `regex` with whatever package
manager you prefer.
Next, attempt to install `pycairo`. If this fails, you're probably
missing dependencies required. See
https://pycairo.readthedocs.io/en/latest/getting_started.html for
details.
Then, install `python-igraph`. Again, missing dependencies are likely -
check https://igraph.org/python/.
Similarly, for `louvain`, detailed installation instructions can be
found from https://louvain-igraph.readthedocs.io/en/latest/install.html.
## Configuration
In the directory, create the folders `logs/` and `output/`.
This prevents the program throwing errors because it doesn't currently
make folders for these.
In `config/`, copy `CONFIG.example.py` to `CONFIG.py` and configure this
as you wish.
### Quick rundown of CONFIG
* `graphml_location`: where output graphs will be saved.
* `log_location`: where log files will be created. "{}" is the current
date.
* `decklist_directory`: directory containing decklists to check for
overlap, when running on `--mode overlap`.
* `aggregate_data_loc`: path to CSV containing the data for all
decklists, for `--mode analysis`.
* `cluster_percentage`: the percentage (interior-total) of weighted
edges each node should have.
* `deck_percentage`: what percentage of a deck should be in cluster X
for it to count as a cluster X deck.
## Usage
Usage is perfomed through the command line. Here, `python3` will be used
to avoid ambiguity, but depending on your installation of Python it may
be `python`.
Running `python3 main.py -h` produces the following:
```
usage: main.py [-h] {overlap,analysis} ...

optional arguments:
  -h, --help          show this help message and exit

mode:
  {overlap,analysis}  Whether the program runs on overlap or analysis: overlap
                      - Discover all files in the decklist_directory specified
                      by CONFIG.py and return the cards that they share.
                      analysis - Cluster decklists
```
`python3 main.py overlap -h` has no additional arguments:
```
usage: main.py overlap [-h]

optional arguments:
  -h, --help  show this help message and exit
```
`python3 main.py analysis -h` produces:
```usage: main.py analysis [-h]
                        [--profile PROFILE PROFILE | --resolution_parameter RESOLUTION_PARAMETER]
                        [--graph] [--no-lands] [--label]

optional arguments:
  -h, --help            show this help message and exit
  --profile PROFILE PROFILE, -p PROFILE PROFILE
                        Run a profile and create a graph of number of clusters
                        against resolution_parameter. The lower and upper
                        bounds are specified after the parameter is passed.
                        This disables the standard output.
  --resolution_parameter RESOLUTION_PARAMETER, -r RESOLUTION_PARAMETER
                        Set the resolution_parameter used in the program to
                        the value passed.
  --graph, -g           Produce a visual for the clusters and a .graphml file
                        in graphml_location (config).
  --no-lands            Remove all land cards from the decks to produce
                        clusters of only nonland cards.
  --label
```
### Example usage
`python3 main.py overlap`
`python3 main.py analysis -r 0.9 --label --no-lands --graph`
## Issues and bug reports
Issues and bug reports, as well as suggestions, can be filed at
https://github.com/Jlobblet/decklist_analyser/issues
## Contributing
Contribution should be done through the repository at
https://github.com/Jlobblet/decklist_analyser.
