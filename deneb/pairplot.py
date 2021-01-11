from typing import Any, Dict, List, Optional, Tuple, Union

import altair as alt
import pandas as pd

from .utils import Chart


def pairplot(
    df: pd.DataFrame,
    field: str = "samples",
    limits: Optional[List[float]] = None,
    values: Optional[List[float]] = None,
    scatter_size: float = 1.5,
    legend: bool = False,
    format: Optional[str] = None,
    color: Optional[Union[str, alt.Color]] = None,
    num_bins: int = 20,
    bar_opacity: float = 0.8,
    clip: bool = True,
    height: Optional[int] = None,
    width: Optional[int] = None,
    interactive: bool = False,
    debug: bool = False,
) -> Chart:
    """Pairplot

    Args:
        df: Samples as as pandas DataFrame. The dataframe needs one column
            labelled with the value of field (defaults to `sample`) which contains the
            sample identifier as a string. All other columns should contain float
            values which will be plotted. The utility function `deneb.np2df` may be
            used to turn a NumPy array into the correct format.
        limits: Limits for plotting (optional)
        values: Tickmark locations (optional)
        scatter_size: Size of scatter points
        legend: Whether or not to show legend
        format: Format string for axis ticks (optional)
        color: Colorscale, e.g. constructed with `deneb.colorscale`
        num_bins: Number of bins
        bar_opacity: Opacity of bars
        clip: Whether to clip
        height: Height of subplot
        width: Width of subplot
        interactive: Turn on interactive mode (experimental)
        debug: Debug mode

    Returns:
        Chart

    Note:
        Build on top of https://github.com/alt-viz/alt/issues/1926.
    """
    labels_dim = [c for c in list(df.columns) if c != field]
    assert len(list(df.columns)) == len(labels_dim) + 1

    if limits is not None:
        assert type(limits) == list
        if type(limits[0]) == float:
            assert len(limits) == 2
            limits_dim = {d: limits for d in labels_dim}
        else:
            assert type(limits[0]) == list
            limits_dim = {d: limits[i] for i, d in enumerate(labels_dim)}

    axis_format = {"format": format} if format is not None else {}

    if color is None:
        color_kwarg = {}
    else:
        color_kwarg = {"color": color}

    def make_upper(r, w, no_x=True, no_y=True, **kwargs):
        enc_x_keywords = {"type": "quantitative"}
        enc_y_keywords = {"type": "quantitative"}

        if limits is not None:
            enc_x_keywords["scale"] = alt.Scale(domain=limits_dim[r], zero=False)
            enc_y_keywords["scale"] = alt.Scale(domain=limits_dim[w], zero=False)
            axis_limits = {"values": limits_dim[r]}
        else:
            axis_limits = {}

        if no_x:
            enc_x_keywords["axis"] = alt.Axis(
                title="", labels=False, domainWidth=0, tickWidth=0,
            )
        else:
            enc_x_keywords["axis"] = alt.Axis(**axis_limits, **axis_format,)
        if no_y:
            enc_y_keywords["axis"] = alt.Axis(
                title="", labels=False, domainWidth=0, tickWidth=0,
            )
        else:
            enc_y_keywords["axis"] = alt.Axis(
                title=w,
                labels=False,
                domainWidth=0,
                tickWidth=0,
                **axis_limits,
                **axis_format,
            )

        if debug:
            enc_x_keywords["axis"] = alt.Axis(title=r, **axis_limits, **axis_format,)
            enc_y_keywords["axis"] = alt.Axis(title=w, **axis_limits, **axis_format,)

        chart = (
            alt.Chart()
            .mark_circle(size=scatter_size, clip=clip)
            .encode(
                alt.X(r, **enc_x_keywords), alt.Y(w, **enc_y_keywords), **color_kwarg,
            )
        )

        if height is not None:
            chart = chart.properties(height=height)

        if width is not None:
            chart = chart.properties(width=width)

        return chart

    def make_lower(r, w, *args, **kwargs):
        return make_upper(r, w, *args, **kwargs)

    def make_diag(r, no_x=True, no_y=True, **kwargs):
        enc_x_keywords = {}
        enc_y_keywords = {}

        enc_x_keywords["type"] = "quantitative"

        if limits is not None:
            enc_x_keywords["scale"] = alt.Scale(domain=limits_dim[r], zero=False)
            axis_limits = {"values": limits_dim[r]}
        else:
            axis_limits = {}

        if no_x:
            enc_x_keywords["axis"] = alt.Axis(
                title="", labels=False, domainWidth=0, tickWidth=0,
            )
        else:
            enc_x_keywords["axis"] = alt.Axis(title=r, **axis_limits, **axis_format,)

        if no_y:
            enc_y_keywords["axis"] = alt.Axis(
                title="", labels=False, domainWidth=0, tickWidth=0,
            )
        else:
            enc_y_keywords["axis"] = alt.Axis(
                title=r, labels=False, domainWidth=0, tickWidth=0, **axis_format,
            )

        if debug:
            enc_x_keywords["axis"] = alt.Axis(title=r, **axis_limits, **axis_format)
            enc_y_keywords["axis"] = alt.Axis(title=r, labels=False, **axis_format)

        chart = alt.Chart()

        if limits is None:
            bin_keywords = {"maxbins": num_bins}
        else:
            bin_keywords = {
                "extent": limits_dim[r],
                "step": (limits_dim[r][1] - limits_dim[r][0]) / num_bins,
            }

        chart = chart.mark_bar(opacity=bar_opacity, clip=clip)
        chart = chart.encode(
            x=alt.X(r, bin=alt.Bin(**bin_keywords), **enc_x_keywords,),
            y=alt.Y("count()", stack=None, **enc_y_keywords),
            **color_kwarg,
        )

        if height is not None:
            chart = chart.properties(height=height)

        if width is not None:
            chart = chart.properties(width=width)

        return chart

    instance = (
        Matrix(df, interactive=interactive)
        .fields(*labels_dim)
        .upper(make_upper)
        .diag(make_diag)
        .lower(make_lower)
    )

    chart = instance.render()

    return chart


class Matrix:
    def __init__(self, data, interactive=False):
        self.data = data
        self.cols = []
        self.rows = []
        self.grid = []
        self.interactive = interactive

    def fields(self, *args):
        self.cols = list(args)
        self.rows = list(args)
        self.grid = [[None for _ in self.rows] for _ in self.cols]
        return self

    def diag(self, make_chart):
        for i, r in enumerate(self.rows):
            no_x = False if i == (len(self.rows) - 1) else True
            no_y = False if i == 0 else True
            self.grid[i][i] = make_chart(r, no_x=no_x, no_y=no_y)
            if self.interactive:
                self.grid[i][i] = self.grid[i][i].interactive()

        return self

    def lower(self, make_chart):
        for i, r in enumerate(self.rows):
            for j, c in enumerate(self.rows):
                if i > j:
                    no_x = False if i == (len(self.rows) - 1) else True
                    no_y = False if j == 0 else True
                    self.grid[i][j] = make_chart(c, r, no_x=no_x, no_y=no_y)
                    if self.interactive:
                        self.grid[i][j] = self.grid[i][j].interactive()

        return self

    def upper(self, make_chart):
        for i, r in enumerate(self.rows):
            for j, c in enumerate(self.cols):
                if j > i:
                    no_x = no_y = True
                    self.grid[i][j] = make_chart(c, r, no_x=no_x, no_y=no_y)
                    if self.interactive:
                        self.grid[i][j] = self.grid[i][j].interactive()

        return self

    def render(self):
        chart = alt.vconcat(data=self.data)
        for i, _ in enumerate(self.rows):
            row = alt.hconcat()
            for j, _ in enumerate(self.cols):
                if self.grid[i][j] is not None:
                    row |= self.grid[i][j]
            if len(row.hconcat) > 0:
                chart &= row

        return chart
