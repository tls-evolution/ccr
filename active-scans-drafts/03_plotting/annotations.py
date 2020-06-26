import matplotlib.transforms as transforms
import matplotlib.pyplot as plt

from config import *

# annotate the different draft versions as rectangles
def add(fig, ax, pvers, svers=ScannerVersions, draw_verticals_only=False, timebar_name_yoffset=0.02):
  trans = None 
  offset = None
  toff = None
  texoff = None
  axoff = None
  axis_to_data = None
  data_to_axis = None

  def initOffset(shift):
    DEFAULT_FONTSIZE = plt.rcParams['font.size']
    nonlocal trans, offset, toff, texoff, axoff, axis_to_data, data_to_axis
    trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
    offset = transforms.ScaledTranslation(0, shift + (DEFAULT_FONTSIZE+2)/72., fig.dpi_scale_trans)
    toff = transforms.ScaledTranslation(0, shift + 0/72., fig.dpi_scale_trans)

    texoff = ax.transAxes + toff
    axoff = ax.transAxes + offset

    axis_to_data = ax.transAxes + ax.transData.inverted()
    data_to_axis = axis_to_data.inverted()

    return shift + (2*(DEFAULT_FONTSIZE+2+2))/72

  def deployment_date_to_plot_date(pd_timestamp):
    # day = 1  # The scanner had influence on the "full month"
    # month = pd_timestamp.month - 1  # result plotting for a month starts at the month before
    # year = pd_timestamp.year
    # if month < 1:
    #   month = 12
    #   year -= 1
    # return pd.Timestamp(year, month, day, 0, 0)

    # ignore day as we normalize all data to the first of the month
    return pd.Timestamp(pd_timestamp.year, pd_timestamp.month, 1)

    # return pd_timestamp


  def addTimeBar(AllVersions, SelectedVersions, Infos, drawV, timebar_name, timebar_name_yoffset, is_scanner=False, draw_verticals_only=False):
    start_axis = {}
    for ver in range(len(AllVersions)):
      dinfo = Infos[AllVersions[ver]]
      x0 = deployment_date_to_plot_date(dinfo["start"])
      if is_scanner:
        # we use the first day of the month to plot the data. Thus, draw the scanner beginning with the previous month
        x0 -= pd.DateOffset(months=1)

      (x0t, _) = data_to_axis.transform_point((float(ax.convert_xunits(x0)), 0))
      start_axis[ver] = x0t
 
      if (x0t >= 0) and (x0t < 1):
        ## Add vertical line through data
        #ax.axvline(x=dinfo["start"], ls=":", c="#c0c0c0", zorder=0)
        pass

    first = False
    for ver in range(len(AllVersions)):
      if not (AllVersions[ver] in SelectedVersions):
        continue
      col = Infos[AllVersions[ver]].get("color")

      name = Infos[AllVersions[ver]]["short"]
      # x0 = deployment_date_to_plot_date(Infos[AllVersions[ver]]["start"])
      # x1 = deployment_date_to_plot_date(Infos[AllVersions[ver+1]]["start"])
      x0t = start_axis[ver]
      x1t = start_axis[ver+1] 

      ## Draw start of draft as annotation
      #first = Infos[AllVersions[ver]].get("first_sample")
      #if first:
      #  (xn, y) = data_to_axis.transform_point((float(ax.convert_xunits(first[0])), ax.convert_yunits(first[1])))
      #  if xn >= x1t:
      #    xf = x1t
      #  else:
      #    xf = x0t
      #  if xf < 0:
      #    xf = 0
      #  ax.annotate('', xy=(xf, y), xytext=(xn, y), xycoords=ax.transAxes, textcoords=ax.transAxes,
      #              arrowprops={'arrowstyle': '-', 'ls': ':', 'lw':  DEFAULT_LINEWIDTH, 'color': col, 'shrinkA': 0, 'shrinkB': 0})

      if (x1t < 0) or (x0t > 1):
        continue

      ## Add vertical line through top
      if (x1t < 1) and drawV:
        if not draw_verticals_only:
          ax.annotate('', xy=(x1t, 1.0), xytext=(x1t, 1.0), xycoords=axoff, textcoords=ax.transAxes,
                      arrowprops={'arrowstyle': '-', 'lw':  DEFAULT_LINEWIDTH, 'shrinkA': 0, 'shrinkB': 0})
        ann = ax.annotate('', xy=(x1t, 0.0), xytext=(x1t, 1.0), xycoords=ax.transAxes, textcoords=ax.transAxes,
                    arrowprops={'arrowstyle': '-', 'lw':  DEFAULT_LINEWIDTH, 'shrinkA': 0, 'shrinkB': 0, 'ls': (0, (5, 5))})
        if PLOT_ANNOTATIONS_BEHIND_VERSION_STACKS:
          ann.set_zorder(0)

      if draw_verticals_only:
        continue

      larrow = '<|'
      rarrow = '|>'
      if x0t < 0:
        rarrow = ''
        x0t = 0
      if x1t > 1:
        x1t = 1
        rarrow = ''

      ax.annotate('', xy=(x0t, 1.0), xytext=(x1t, 1.0), xycoords=axoff,
                arrowprops={'arrowstyle': larrow + '-' + rarrow, 'color': col, 'lw': DEFAULT_LINEWIDTH
                })
      if not first:
        ax.annotate(" " + timebar_name, xy=(x0t, 1.0 + timebar_name_yoffset), xycoords=axoff, ha='left', va='bottom')
        first = True

      t = ax.annotate("\\textbf{" + name + "}", xy=((x0t + x1t)*0.5, 1.0), xycoords=texoff, ha='center', va='bottom', color=col)

      ## Colorize backgrounds
      #rect = mpatches.Rectangle((x0,0), width=x1-x0, height=1,
      #                       transform=trans, color=col,
      #                       alpha=0.1)
      #ax.add_patch(rect)

  yoff = initOffset(0.0/72.0)
  addTimeBar(AllVersions=DraftVersions, SelectedVersions=pvers, Infos=DraftInfo, drawV=True, timebar_name="TLS 1.3 draft history", timebar_name_yoffset=timebar_name_yoffset, draw_verticals_only=draw_verticals_only)
  if not draw_verticals_only:
    initOffset(yoff)
    addTimeBar(AllVersions=ScannerMajors + ["FUTURE"], SelectedVersions=ScannerMajors, Infos=ScannerInfo, drawV=False, timebar_name="Highest supported draft (scanner)", timebar_name_yoffset=timebar_name_yoffset, is_scanner=True)

