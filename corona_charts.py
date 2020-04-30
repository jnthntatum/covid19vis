import csv
import requests
import matplotlib as m
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict, Sequence
from argparse import ArgumentParser
import sys

BATCH = [
    ("Washington", "wa"),
    ("New York", "ny"),
    ("Colorado", "co"),
    ("California", "ca"),
    ("New Jersey", "nj"),
    ("Oregon", "or"),
    ("Nevada", "nv")
]

WEST_COAST_PACT = [
    ("Washington", "wa"),
    ("Colorado", "co"),
    ("California", "ca"),
    ("Oregon", "or"),
    ("Nevada", "nv")
]


def read_from_master(fname):
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/{}".format(fname)
    response = requests.get(url)
    print(response.text[0:1024])
    return response.text.strip().split("\n")


def read_from_cwd(fname):
    return list(open(fname))


def parse(raw: Sequence[str]) -> Tuple[List[str], List[List[str]], List[List[float]], Dict[str, int]]:
    """Returns a tuple of (hdrs, data, timeseries, column idx map)"""
    data = list(csv.reader(raw))

    print(len(data))
    print(len(data[0]))
    # check that it's actually a matrix
    print(set(len(r) for r in data))

    hdrs, data = data[0], data[1:]

    ts = [[float(x) for x in r[12:]] for r in data]
    col = {l: i for i, l in enumerate(hdrs)}
    return hdrs, data, ts, col


def T(m):
    j_max = len(m[0])
    i_max = len(m)
    t = [[0] * i_max for _ in range(j_max)]
    for ip in range(j_max):
        for jp in range(i_max):
            t[ip][jp] = m[jp][ip]
    return t


def lsub(lhs, rhs):
    return [x - rhs[i] for i, x in enumerate(lhs)]


def compute_wma(series, window=3):
    assert(window >= 1)
    buff = [0] * (window - 1) + series
    return [sum(buff[i+j] for j in range(window)) / window for i in range(len(series))]


def stagger_labels(labels, staggering=3):
    return [l if (i % staggering == 0) else "" for i, l in enumerate(labels)]


def draw(fname, dates, dpd, wma, title=""):
    labels = stagger_labels(dates)
    fig, ax = plt.subplots(figsize=(6,4))
    dc = ax.bar(dates, dpd, color='orange')
    avg, = ax.plot(dates[:-3], wma[3:])
    ax.set_xticklabels(labels, rotation="vertical", fontsize=6)
    ax.legend((dc, avg), ("(est.) daily count", "7 day average"))
    ax.set_title(title)
    fig.savefig(fname, dpi=600)

def wma_slice(series, idxs):
    slice_ts = [series[i] for i in idxs]
    slice_delta_ts = [lsub(r, [0] + r) for r in slice_ts]
    deltas = [sum(r) for r in T(slice_delta_ts)]
    wma = compute_wma(deltas, 7)
    return deltas, wma


def outfile(prefix, mode):
    return "{}.{}.svg".format(prefix, mode)


def eq(arg):
    def pred(x):
        return x == arg
    return pred


def is_wcp(x):
    return x in [state for state, abbrv in WEST_COAST_PACT]


def title(mode, subtitle):
    if mode == "confirmed":
        t = "Confirmed Cases"
    else:
        t = "Deaths"

    return "{} -- {}".format(t, subtitle)


def load_and_draw(mode, slices):
    filename = 'time_series_covid19_{}_US.csv'.format(mode)
    raw = read_from_master(filename)
    hdrs, data, ts, col = parse(raw)
    dates = hdrs[12:]

    def draw_slice(filter_field='iso3', filter_pred=eq('USA'), prefix='us'):
        slice_idxs = [i for i, row in enumerate(data) if filter_pred(row[col[filter_field]])]
        slice_deltas, slice_wma = wma_slice(ts, slice_idxs)

        draw(outfile(prefix, mode), dates, slice_deltas, slice_wma, title=title(mode, prefix))

    draw_slice()
    draw_slice(filter_field="Province_State", filter_pred=is_wcp, prefix="west_coast_pact")
    for state, state_abrv in slices:
        draw_slice(filter_field="Province_State", filter_pred=eq(state), prefix=state_abrv)

def main(args):
    mode = args.mode
    if mode == "both":
        modes = ["confirmed", "deaths"]
    else:
        modes = [mode] 
    for mode in modes:
        load_and_draw(mode, BATCH)
        

def one_shot_args(parser):
    # TODO add subcommand for this
    parser.add_argument("-f", dest="filter", choices=["Province_State"], default="Province_State")
    parser.add_argument("-v", dest="filter_value", help="filter value", default="Washington")
    parser.add_argument("-n", dest="slice_prefix", help="filename prefix", default="wa")

def parse_args():
    parser = ArgumentParser(sys.argv[0])
    parser.add_argument("mode", choices=['deaths', 'confirmed', 'both'])
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())