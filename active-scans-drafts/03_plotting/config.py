import pandas as pd

from enum import Enum

fig_width = 252 # in pt
fig_height = 100 # in pt

dtp_per_inch = 72.27

DEFAULT_MARKERSIZE = 1
DEFAULT_LINEWIDTH = 1
DOT_MISSING = True


class StackedType(Enum):
  Hatched = 1,
  Filled = 2,
  HatchedAndFilled = 3,
  Stroked = 4,
  HatchedAndStroked = 5,

STACKED_TYPE = StackedType.HatchedAndStroked

FoundVersions = ['TLSv1.3', 'TLSv1.3draft18', 'TLSv1.3draft19', 'TLSv1.3draft21', 'TLSv1.3draft22',
                 'TLSv1.3draft23', 'TLSv1.3draft26', 'TLSv1.3draft28']

MajorVersions = ['TLSv1.3', 'TLSv1.3draft18', 'TLSv1.3draft22', 'TLSv1.3draft23']

DraftVersions = ['TLSv1.2',
                 'TLSv1.3draft18', 'TLSv1.3draft19', 'TLSv1.3draft20', 'TLSv1.3draft21',
                 'TLSv1.3draft22', 'TLSv1.3draft23', 'TLSv1.3draft24', 'TLSv1.3draft25',
                 'TLSv1.3draft26', 'TLSv1.3draft27', 'TLSv1.3draft28', 'TLSv1.3', 'FUTURE'
]

Color10 = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#1a55FF']

DraftInfo = {
        'TLSv1.2'       : { 'start': pd.Timestamp(2008, 8, 1, 0, 0),   'short': 'RFC', 'marker': '.', 'color': '#000000',  'hatch': 'x'*5},
	'TLSv1.3draft18': { 'start': pd.Timestamp(2016, 10, 26, 0, 0), 'short': '18',  'marker': '.', 'color': Color10[1], 'hatch': 'x'*5},
	'TLSv1.3draft19': { 'start': pd.Timestamp(2017, 3, 10, 0, 0),  'short': '19',  'marker': '.', 'color': Color10[4], 'hatch': 'x'*5},
	'TLSv1.3draft20': { 'start': pd.Timestamp(2017, 4, 28, 0, 0),  'short': '20',  'marker': '.', 'color': '#000000' , 'hatch': 'x'*5},
	'TLSv1.3draft21': { 'start': pd.Timestamp(2017, 7, 3, 0, 0),   'short': '21',  'marker': '.', 'color': Color10[5], 'hatch': 'x'*5},
	'TLSv1.3draft22': { 'start': pd.Timestamp(2017, 11, 29, 0, 0), 'short': '22',  'marker': '.', 'color': Color10[2], 'hatch': 'x'*5},
        'TLSv1.3draft23': { 'start': pd.Timestamp(2018, 1, 5, 0, 0),   'short': '23',  'marker': '.', 'color': Color10[3], 'hatch': 'x'*5},
        'TLSv1.3draft24': { 'start': pd.Timestamp(2018, 2, 15, 0, 0),  'short': '24',  'marker': '.', 'color': '#000000' , 'hatch': 'x'*5},
        'TLSv1.3draft25': { 'start': pd.Timestamp(2018, 3, 2, 0, 0),   'short': '25',  'marker': '.', 'color': '#000000' , 'hatch': 'x'*5},
        'TLSv1.3draft26': { 'start': pd.Timestamp(2018, 3, 4, 0, 0),   'short': '26',  'marker': '.', 'color': Color10[6], 'hatch': 'x'*5},
        'TLSv1.3draft27': { 'start': pd.Timestamp(2018, 3, 18, 0, 0),  'short': '27',  'marker': '.', 'color': '#000000' , 'hatch': 'x'*5},
        'TLSv1.3draft28': { 'start': pd.Timestamp(2018, 3, 20, 0, 0),  'short': '28',  'marker': '.', 'color': Color10[7], 'hatch': 'x'*5},
	'TLSv1.3'       : { 'start': pd.Timestamp(2018, 8, 1, 0, 0),   'short': 'RFC', 'marker': '.', 'color': Color10[0], 'hatch': 'x'*5},
        'FUTURE'        : { 'start': pd.Timestamp(2100, 1, 1, 0, 0),   'short': 'Dummy'},
}

Events = [
  {'start': pd.Timestamp(2017, 12, 13, 0, 0), 
   'text' : 'Chrome migrated to Draft22',
   'detail': 'https://github.com/chromium/chromium/commit/49408842cea256b67f83ecb32283949552f99b87',
  },
  {'start': pd.Timestamp(2018, 1, 4, 0, 0),
   'text' : 'Firefox migrated to Draft22',
   'detail': 'https://bugzilla.mozilla.org/show_bug.cgi?id=1418862',
  },
  {'start': pd.Timestamp(2018, 2, 19, 0, 0),
   'text' : 'Scanner update',
   'detail': 'Updated scanner to rabbitQueue_tls-13-all-recent_since-2018-02-19',
  },
  {'start': pd.Timestamp(2018, 3, 6, 0, 0),
   'text' : 'Scanner update',
   'detail': 'Updated scanner to rabbitQueue_tls-13-all-recent_since-2018-03-06',
  },
  {'start': pd.Timestamp(2018, 7, 24, 0, 0),
   'text' : 'Chrome release',
   'detail': 'Chrome 68 release, Flags any http as insecure',
  },
  {'start': pd.Timestamp(2019, 1, 29, 0, 0),
   'text' :'Chrome release',
   'detail': 'Chrome 72 release. Removal of HTTP-Based Public Key Pinning. Deprecation of TLS 1.0 and TLS 1.1',
  },
  {'start': pd.Timestamp(2019, 2, 26, 0, 0),
   'text' : 'Scanner update',
   'detail': 'Updated scanner to rabbitQueue_tls-13-all-recent_since-2019-02-26',
  },
  {'start': pd.Timestamp(2019, 3, 5, 0, 0),
   'text' : 'Scanner update',
   'detail': 'Updated scanner to rabbitQueue_tls-13-all-recent_since-2019-03-05',
  },
  {'start': pd.Timestamp(2019, 1, 27, 0, 0),
   'text' : 'Cloudflare migration',
   'detail': 'Cloudflare migrated to TLS 1.3 as Chrome 72 rolled out RFC support. WordPress still offering Draft28',
  },
]

ScannerMajors = ['V0', 'V1', 'V2', 'V3']
ScannerVersions = ['V0', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
ScannerVersionsF = ScannerVersions + ['FUTURE']
ScannerInfo = {
  # discrepancy: already saw d23 on 2018,1,21 e.g. on soccer-A-www => v2 was deployed
  'V0'       : { 'start': pd.Timestamp(2008, 8, 1, 0, 0),  'short': '18', 'color': DraftInfo['TLSv1.3draft18']['color']},
  'V1'       : { 'start': pd.Timestamp(2018, 2, 19, 0, 0), 'short': '22', 'color': DraftInfo['TLSv1.3draft22']['color']}, #d22 till here
  'V2'       : { 'start': pd.Timestamp(2018, 3, 6, 0, 0),  'short': '23', 'color': DraftInfo['TLSv1.3draft23']['color']}, #d23 since here
  'V3'       : { 'start': pd.Timestamp(2019, 2, 26, 0, 0), 'short': 'RFC', 'color': DraftInfo['TLSv1.3']['color']}, # signal up to d28
  'V4'       : { 'start': pd.Timestamp(2019, 3, 5, 0, 0),  'short': 'RFC', 'color': DraftInfo['TLSv1.3']['color']}, # chacha20 fix
  'V5'       : { 'start': pd.Timestamp(2019, 3, 19, 0, 0), 'short': 'RFC', 'color': DraftInfo['TLSv1.3']['color']}, # keyshare fix for backwards compat
  'V6'       : { 'start': pd.Timestamp(2019, 6, 14, 0, 0), 'short': 'RFC', 'color': DraftInfo['TLSv1.3']['color']}, # added quantum safe ciphers
  'FUTURE'   : { 'start': pd.Timestamp(2100, 1, 1, 0, 0),  'short': 'Dummy'},
}

