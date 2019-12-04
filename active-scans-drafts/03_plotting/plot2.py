from pathlib import Path
import json
import math
import copy

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np

from config import *
import annotations

fig_width = 241 # in pt
fig_height = 75 #100 # in pt

#plotting_sets = ['full_latest.',  'full_preferred_over_sh_latest.', 'full_or_sh_latest.', 'full_and_sh_latest.']
plotting_sets = [
  'all.',
  'full_preferred_over_sh_latest.',
  'full_latest.'
  ]

def loadFile(f):
  """Loads a single json file as row for a DataFrame
  """
  date = pd.to_datetime(f.name.split('.', 1)[0], format='%Y_%m')
  with open(f, 'r') as json_file:
    js = json.loads(json_file.read())
    js['date'] = date
    return js


def gatherDataForZone(path):
  """Loads all files of form 2019_01.json from the given path to a pandas DataFrame
  """
  f = [f for f in path.rglob('20??_??.json')]
  f.sort()
  data = [loadFile(f) for f in f]
  frame = pd.DataFrame(json_normalize(data))
  frame.set_index('date', inplace=True)
  # frame = frame.resample('m').ffill() # replicate last known month for missing ones
  return frame


def makeRelativeTo13(df):
  # makes all 1.3 subversions within "full SH full-or-SH and full-and-SH" relative to their total 1.3 counts
  ndf = pd.DataFrame(index=df.index)
  #for subset in ['full.', 'SH.', 'full-or-SH.', 'full-and-SH.']:
  #for subset in ['full_latest.',  'full_preferred_over_sh_latest.', 'full_or_sh_latest.', 'full_and_sh_latest.']:
  for subset in plotting_sets:

    df[subset + 'TLS1v.3Total'] = sum([df[subset + x] for x in FoundVersions])  
    for x in FoundVersions:
      ndf[subset + x] = df[subset + x] / df[subset + 'TLS1v.3Total']
  ndf_percent = ndf.iloc[:,:].mul(100, axis=0)
  return ndf_percent

def makeRelativeToAll(df):
  # makes everything relative to the total count
  df_fraction = df.iloc[:,:].div(df['all'], axis=0) # just divide all colums by 'Total' column
  df_percent = df_fraction.iloc[:,:].mul(100, axis=0)
  return df_percent

def configStacks(stacks, pvers, stacktypes=None):
  """Configs the Stack according to given colors/configs in config.py
  """
  pal = [DraftInfo[ver]['color'] for ver in pvers]
  hatches = [DraftInfo[ver]['hatch'] for ver in pvers]

  for i in range(len(stacks)):
    stack = stacks[i]
    hatch = hatches[i]
    color = pal[i]
    # stack.set_facecolor(color)

    typ = STACKED_TYPE
    if stacktypes:
      typ = stacktypes[i]

    if typ == StackedType.Hatched:
      stack.set_facecolor((1,1,1,1))

    if typ in [StackedType.Stroked, StackedType.HatchedAndStroked]:
      # stack.set_edgecolor(color)
      stack.set_facecolor((1,1,1,1))
    # else:
    #   stack.set_edgecolor((0,0,0,1))

    if typ in [StackedType.Hatched, StackedType.HatchedAndFilled, StackedType.HatchedAndStroked]:
      stack.set_hatch(hatch)

    stack.set_zorder(2 - (i+1)/len(stacks))

def genPlot_single(path, domain_list, args):
  df = gatherDataForZone(Path(path))
  ndf = pd.DataFrame(index=df.index)

  vers = [
    # 'SSLv3',
    # 'TLSv1.0',
    # 'TLSv1.1',
    # 'TLSv1.2',
    'TLSv1.3draft18',
    'TLSv1.3draft19',
    'TLSv1.3draft20',
    'TLSv1.3draft21',
    'TLSv1.3draft22',
    'TLSv1.3draft23',
    'TLSv1.3draft24',
    'TLSv1.3draft25',
    'TLSv1.3draft26',
    'TLSv1.3draft27',
    'TLSv1.3draft28',
    'TLSv1.3'
    ]
  style = []
  for v in vers:
    ndf["full/" + v] = df['full_latest.' + v] / df['all'] * 100
    ndf["SH/" + v] = (df['full_preferred_over_sh_latest.' + v] - df['full_latest.' + v]) / df['all'] * 100


  nonnullCols = (ndf != 0).any(axis=0)
  foundVers = [x.split('/',1)[1] for x in nonnullCols[nonnullCols].index]
  ndf = ndf.loc[:, nonnullCols]
  style = []
  for col in ndf.columns:
    if col.startswith("full/"):
      style.append(StackedType.Filled)
    elif col.startswith("SH/"):
      style.append(StackedType.HatchedAndStroked)
    else:
      raise NameError("Neither full nor SH: {}".format(col[0]))
  colors = [DraftInfo[ver]['color'] for ver in foundVers]

  fig, ax = plt.subplots(1, 1)

  if not ndf.empty:
    ndf.plot.area(ax = ax, legend=True, color=colors, linewidth=0, fontsize=15, stacked=True)
    configStacks(ax.collections, foundVers, style)

  pd.set_option('display.max_columns', 1000)
  print(ndf)
  xticks_positions = ndf.index
  xticks_labels = [p.strftime('%Y-%m') for p in xticks_positions]
  ax.set_xticks(xticks_positions)
  ax.set_xticklabels(xticks_labels,
    horizontalalignment='right',  # 'center',
    verticalalignment='top', # baseline
    rotation=60,
    usetex=False
    )
  xticks_label_offset = 0.03
  for xtl in ax.get_xticklabels():
    xtl.set_y(xtl.get_position()[1] - xticks_label_offset)
  ax.set_xticks([], minor=True)

  ax.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%d'))

  # ax.set_title("{}".format(domain_list.lstrip('_')), pad=30)
  ax.set_xlabel("")
  ax.set_ylabel("Percent connections per month", fontsize=15)
  if args.nonfixedylimit:
    ax.set_ylim([None, min(119, ax.get_ylim()[1]*1.25)]) # AS plots
  else:
    ax.set_ylim([None, 19]) # DNS zone plots
  ax.set_xlim([pd.Timestamp(2017, 10, 1, 0, 0), pd.Timestamp(2019, 4, 1, 0, 0)])

  params = {'backend': 'ps',
            # 'axes.labelsize': 20, # fontsize for x and y labels (was 10)
            # 'axes.titlesize': 20,
            'font.size': 15, # was 10
            'legend.fontsize': 15, # was 10
            # 'xtick.labelsize': 10,
            # 'ytick.labelsize': 10,
            'text.usetex': True,
            # Setting text.latex.preview to True helps with the vertical alignment of legend label text
            # that uses LaTeX subscript, e.g., 'x_1'
            # https://stackoverflow.com/questions/40424249/vertical-alignment-of-matplotlib-legend-labels-with-latex-math
            # 'text.latex.preview': True,
            'figure.figsize': [fig_width, fig_height],
            'font.family': 'serif',
            'font.serif': 'Times'
  }
  mpl.rcParams.update(params)

  fig.subplots_adjust(left=0.11)
  fig.subplots_adjust(bottom=0.18)
  fig.subplots_adjust(right=0.96)
  fig.subplots_adjust(top=0.88)

  handles, labels = ax.get_legend_handles_labels()
  handles_filtered = []
  labels_filtered = []
  while len(labels):
    label = labels.pop(0)
    handle = handles.pop(0)

    # make all handles non-hatched; don't change the original as it has influence on the plotting
    handle = copy.copy(handle)
    handle.set_hatch(None)
    handle.set_color(handle.get_ec())

    label = label.split('/',1)[1] # strip of full / SH type
    if label not in labels_filtered:
      labels_filtered.append(label)
      handles_filtered.append(handle)
  legend_ncols = 2
  legend = ax.legend(
        handles_filtered,
        labels_filtered,
        loc='upper left',
        # loc='upper center',
        # ncol=,
        ncol=legend_ncols,
        # bbox_to_anchor=legend_bbox_to_anchor,
        # borderpad=0.2,
        # columnspacing=0.8,
        # handlelength=1,
        # handletextpad=0.2
    )

  # annotations.add(plt.gcf(), ax, foundVers)
  vers_to_annotate = vers
  vers_to_annotate.remove('TLSv1.3draft25')
  vers_to_annotate.remove('TLSv1.3draft26')
  vers_to_annotate.remove('TLSv1.3draft27')
  annotations.add(plt.gcf(), ax, vers_to_annotate)

  return fig


def genPlot_separate(path, domain_list, args):
  df = gatherDataForZone(Path(path))
  df.loc[df.index[0] - pd.DateOffset(months=1)] = pd.Series()

  vers = FoundVersions
  if args.tls12:
    vers = vers + ['TLSv1.2']
  if vers[0] == 'TLSv1.3':
    vers = vers[1:] + [vers[0]] # plot TLS 1.3 last


  nrows = len(plotting_sets)
  ncols = 1
  fig, axs = plt.subplots(nrows, ncols)
  axpres = []
  row_index = 0
  col_index = 0
  for subset in plotting_sets:
    if nrows > 1 and ncols > 1:
      axpres.append({'ax': axs[row_index,col_index], 'pre': subset.rstrip('.')})
    else:
      axpres.append({'ax': axs[row_index], 'pre': subset.rstrip('.')})
    col_index += 1
    if col_index == ncols:
      row_index += 1
      col_index = 0
  for axpre in axpres:
    ax = axpre['ax']
    if axpre['pre'] == 'all':
      df['all'].plot(ax = axpre['ax'], legend=False)
    else:
      df = makeRelativeToAll(df)
      #df = makeRelativeTo13(df)

      subdf = df[[axpre['pre'] + '.' + x for x in vers]]

      nonnullCols = (subdf != 0).any(axis=0)
      foundVers = [x.split('.',1)[1] for x in nonnullCols[nonnullCols].index]
      colors = [DraftInfo[ver]['color'] for ver in foundVers]
      subdf = subdf.loc[:, nonnullCols]
      if not subdf.empty:
        subdf.plot.area(ax = axpre['ax'], legend=False, color=colors, linewidth=0, stacked=True)
        configStacks(ax.collections, foundVers)
      annotations.add(plt.gcf(), ax, foundVers)

    ax.set_title("{} ({})".format(axpre['pre'].lstrip('_'), domain_list.lstrip('_')), pad=30)
    ax.set_ylabel("Percent connections per month".format())

  y_lim_max = max([(axpre['ax'].get_ylim()[1] if axpre['pre'] not in ['all'] else 0) for axpre in axpres])
  for axpre in axpres:
    if axpre['pre'] not in ['all']:
      axpre['ax'].set_ylim([None, y_lim_max])


  plt.subplots_adjust(hspace=0.85)

  params = {'backend': 'ps',
            'axes.labelsize': 7, # fontsize for x and y labels (was 10)
            'axes.titlesize': 5,
            'font.size': 5, # was 10
            'legend.fontsize': 7, # was 10
            'xtick.labelsize': 6,
            'ytick.labelsize': 6,
            'text.usetex': True,
            # Setting text.latex.preview to True helps with the vertical alignment of legend label text
            # that uses LaTeX subscript, e.g., 'x_1'
            # https://stackoverflow.com/questions/40424249/vertical-alignment-of-matplotlib-legend-labels-with-latex-math
            # 'text.latex.preview': True,
            'figure.figsize': [fig_width * ncols, fig_height * nrows],
            'font.family': 'serif',
            'font.serif': 'Times'
  }
  mpl.rcParams.update(params)

  fig.subplots_adjust(left=0.07)
  fig.subplots_adjust(bottom=0.15)
  fig.subplots_adjust(right=0.98)
  fig.subplots_adjust(top=0.88)

  return fig

if __name__== "__main__":
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('--basedir', help='base dir to search files within')
  parser.add_argument('--separate', action='store_true', default=False, help='print separately')
  parser.add_argument('--tls12', action='store_true', default=False, help='include TLS 1.2 in plot')
  parser.add_argument('--nonfixedylimit', action='store_true', default=False, help='include TLS 1.2 in plot')
  args = parser.parse_args()
  if args.basedir:
    domain_list = args.basedir.split('/')[-1]

    if args.separate:
      fig = genPlot_separate(args.basedir, domain_list, args)
      plt.show()
      # fig.savefig('plot_{}_separate.pdf'.format(domain_list))
    else:
      fig = genPlot_single(args.basedir, domain_list, args)
      # plt.show()
      fig.savefig('plot_{}_single.pdf'.format(domain_list))
