#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                  __               __
#?            _____/ /_  ____ ______/ /______
#?           / ___/ __ \/ __ `/ ___/ __/ ___/
#?          / /__/ / / / /_/ / /  / /_(__  )
#?          \___/_/ /_/\__,_/_/   \__/____/
#?
#?
#? Name:        charts.py
#? Purpose:     chart widgets: a matplotlib Pareto chart and a Qt Charts donut, both theme-aware.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     11/11/2025
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
import  functools
import  numpy                       as      np

from    PyQt5.QtChart               import  QChart, QChartView, QLegend, QPieSeries
from    PyQt5.QtCore                import  QMargins, Qt
from    PyQt5.QtGui                 import  QColor, QCursor, QFont, QPainter, QPen
from    PyQt5.QtWidgets             import  QToolTip, QVBoxLayout, QWidget

#? Import matplotlib's Qt backend only after PyQt5 so it binds to the same Qt.
from    matplotlib.backends.backend_qtagg   import  FigureCanvasQTAgg, NavigationToolbar2QT
from    matplotlib.figure           import  Figure
from    matplotlib.lines            import  Line2D
from    matplotlib.patches          import  Patch
from    matplotlib.ticker           import  FuncFormatter, PercentFormatter

from    lib.theme                   import  SERIES_COLORS, Theme
#?----------------------------------------------------------------------------------------------------------------------------------------
class Fmt:
    """Short text for chart labels and axis ticks."""

    @staticmethod
    def short(text: str, limit: int = 18) -> str:
        return text if len(text) <= limit else text[: limit - 1] + "…"

    @staticmethod
    def number(v: float) -> str:
        if abs(v) >= 1e6:
            return f"{v / 1e6:,.1f}M"
        if abs(v) >= 1e4:
            return f"{v / 1e3:,.0f}k"
        return f"{v:,.0f}" if float(v).is_integer() else f"{v:,.2f}"
#?----------------------------------------------------------------------------------------------------------------------------------------
class ParetoChart(QWidget):
    """Bars sorted descending + cumulative-percentage line, vital few highlighted."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result        = None
        self._palette       = Theme.get_palette("dark")
        self._hover_index   = None

        self.figure         = Figure(layout="constrained")
        self.canvas         = FigureCanvasQTAgg(self.figure)
        self.canvas.setMinimumSize(200, 160)
        self.canvas.mpl_connect("motion_notify_event", self._on_hover)

        self._layout        = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 4, 8, 8)
        self._layout.setSpacing(0)
        self.toolbar        = None
        self._make_toolbar()
        self._layout.addWidget(self.canvas, 1)

    def _make_toolbar(self):
        """The toolbar picks icon colours from the palette when built, so rebuild it per theme."""
        if self.toolbar is not None:
            self._layout.removeWidget(self.toolbar)
            self.toolbar.deleteLater()
        self.toolbar        = NavigationToolbar2QT(self.canvas, self)
        self._layout.insertWidget(0, self.toolbar)

    def set_palette(self, palette: dict):
        self._palette       = palette
        self._make_toolbar()
        self._draw()

    def plot(self, result):
        self._result        = result
        self._draw()

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Drawing
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _draw(self):
        p, r, fig           = self._palette, self._result, self.figure
        fig.clear()
        fig.set_facecolor(p["surface"])
        if r is None:
            self.canvas.draw_idle()
            return

        n                   = len(r.labels)
        x                   = np.arange(n)
        ax                  = fig.add_subplot(111)
        ax2                 = ax.twinx()

        colors              = [p["accent"] if i < r.vital_few else p["chart_muted"] for i in range(n)]
        ax.bar(x, r.values, color=colors, width=0.68, zorder=2)
        ax2.plot(x, r.cumulative, color=p["chart_secondary"], marker="o", markersize=4.5, linewidth=2, zorder=3)
        ax2.axhline(80, color=p["chart_secondary"], linestyle=(0, (4, 4)), linewidth=1, alpha=0.7)

        labels              = [Fmt.short(lab) for lab in r.labels]
        rotate              = n > 6 or max(len(lab) for lab in labels) > 10
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=40 if rotate else 0, ha="right" if rotate else "center", rotation_mode="anchor")
        ax.set_xlim(-0.6, n - 0.4)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: Fmt.number(v)))
        ax2.set_ylim(0, 105)
        ax2.yaxis.set_major_formatter(PercentFormatter(decimals=0))

        ax.set_facecolor(p["surface"])
        ax2.set_facecolor("none")
        ax.grid(axis="y", color=p["border"], linewidth=0.8)
        ax.set_axisbelow(True)
        for axis in (ax, ax2):
            for side, spine in axis.spines.items():
                spine.set_visible(side == "bottom")
                spine.set_color(p["border"])
            axis.tick_params(colors=p["text_muted"], labelsize=9, length=0, pad=6)
        ax.set_ylabel(r.value, color=p["text_muted"], fontsize=9.5)
        ax2.set_ylabel("Cumulative share", color=p["text_muted"], fontsize=9.5)
        ax.set_title(f"{r.value} by {r.category}", loc="left", color=p["text"], fontsize=12, fontweight="bold", pad=10)

        handles             = [Patch(color=p["accent"], label="Vital few (≤ 80 %)"),
                               Patch(color=p["chart_muted"], label="Others"),
                               Line2D([], [], color=p["chart_secondary"], marker="o", markersize=4.5,
                                      linewidth=2, label="Cumulative %")]
        fig.legend(handles=handles, loc="outside upper right", ncols=3, frameon=False, fontsize=9, labelcolor=p["text_muted"])
        self.canvas.draw_idle()

    def _on_hover(self, event):
        r                   = self._result
        index               = None
        if r is not None and event.inaxes is not None and event.xdata is not None:
            i               = int(round(event.xdata))
            if 0 <= i < len(r.labels) and abs(event.xdata - i) <= 0.4:
                index       = i
        if index == self._hover_index:
            return
        self._hover_index   = index
        if index is None:
            QToolTip.hideText()
            return
        QToolTip.showText(QCursor.pos(),
                          f"<b>{r.labels[index]}</b><br>{r.value}: {r.values[index]:,.6g}"
                          f"<br>Cumulative: {r.cumulative[index]:.1f} %", self.canvas)
#?----------------------------------------------------------------------------------------------------------------------------------------
class DonutChart(QChartView):
    """Share of the total per category; slices pop out on hover."""

    TOP                     = 8                                                        # slices shown; the rest are merged into 'Other'

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result        = None
        self._palette       = Theme.get_palette("dark")
        chart               = QChart()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setAnimationDuration(500)
        chart.setBackgroundRoundness(0)
        chart.layout().setContentsMargins(0, 0, 0, 0)
        chart.setMargins(QMargins(12, 12, 12, 12))
        legend              = chart.legend()
        legend.setAlignment(Qt.AlignRight)
        legend.setMarkerShape(QLegend.MarkerShapeCircle)
        title_font          = QFont(self.font())
        title_font.setPointSizeF(12)
        title_font.setWeight(QFont.DemiBold)
        chart.setTitleFont(title_font)
        self.setChart(chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setFrameShape(QChartView.NoFrame)
        self.setMinimumSize(200, 160)

    def set_palette(self, palette: dict):
        self._palette       = palette
        bg                  = QColor(palette["surface"])
        self.setBackgroundBrush(bg)
        self.chart().setBackgroundBrush(bg)
        self.chart().setTitleBrush(QColor(palette["text"]))
        self.chart().legend().setLabelColor(QColor(palette["text"]))
        self._rebuild()

    def plot(self, result):
        self._result        = result
        self._rebuild()

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Drawing
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _rebuild(self):
        chart, r, p         = self.chart(), self._result, self._palette
        chart.removeAllSeries()
        chart.setTitle("")
        if r is None:
            return
        labels, values      = list(r.labels), list(r.values)
        if len(labels) > self.TOP:
            labels          = labels[: self.TOP - 1] + [f"Other ({len(labels) - self.TOP + 1})"]
            values          = values[: self.TOP - 1] + [float(sum(values[self.TOP - 1:]))]
        series              = QPieSeries()
        series.setHoleSize(0.55)
        series.setPieSize(0.8)
        border              = QPen(QColor(p["surface"]), 2)
        for i, (label, value) in enumerate(zip(labels, values)):
            pct             = value / r.total * 100
            slice_          = series.append(f"{Fmt.short(label, 22)}  {pct:.1f}%", value)
            slice_.setColor(QColor(SERIES_COLORS[i % len(SERIES_COLORS)]))
            slice_.setPen(border)
            slice_.setLabelColor(QColor(p["text"]))
            slice_.setLabelVisible(False)
            slice_.setExplodeDistanceFactor(0.06)
            slice_.hovered.connect(functools.partial(self._on_hover, slice_))
        chart.addSeries(series)
        chart.setTitle(f"Share of {r.value} by {r.category}")
        self._update_legend()

    @staticmethod
    def _on_hover(slice_, state):
        slice_.setExploded(state)
        slice_.setLabelVisible(state)

    def _update_legend(self):
        wide                = self.width() > self.height() * 1.3
        self.chart().legend().setAlignment(Qt.AlignRight if wide else Qt.AlignBottom)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_legend()
#?----------------------------------------------------------------------------------------------------------------------------------------
