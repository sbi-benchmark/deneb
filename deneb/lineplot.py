from typing import Any, Dict, List, Optional, Tuple, Union

import altair as alt
import pandas as pd

from .utils import Chart


def lineplot(
    df,
    x: str,
    y: str,
    label_orient: str = "top",
    title_orient: str = "bottom",
    column: Optional[str] = None,
    column_title: str = "",
    column_sort: Optional[List[str]] = None,
    column_labels: bool = True,
    column_keywords: Dict[str, Any] = {},
    row: Optional[str] = None,
    row_title: str = "",
    row_sort: Optional[List[str]] = None,
    row_labels: bool = True,
    row_keywords: Dict[str, Any] = {},
    aggregate: Optional[str] = "mean",
    points: bool = True,
    lines: bool = True,
    errorbars: bool = True,
    error_extent: str = "stdev",
    limits: Optional[List[float]] = None,
    independent_x: bool = True,
    independent_y: bool = False,
    log_y: bool = False,
    y_axis: Optional[alt.Axis] = None,
    spacing: int = 5,
    color: Optional[Union[str, alt.Color]] = None,
    shape: Optional[Union[str, alt.Shape]] = None,
    detail: Optional[Union[str, alt.Detail]] = None,
    height: Optional[int] = None,
    width: Optional[int] = None,
) -> Chart:
    """Produces lineplot with optional errorbars and facets

    Args:
        df: Dataframe
        x: Shorthand for x
        y: Shorthand for y
        label_orient: Orientation of column labels
        title_orient: Orientation of column title
        column: Shorthand for columns (optional) which are faceted
        column_title: Title text for columns displayed 
        column_sort: Optional sorting for columns
        column_labels: Whether header labels should be displayed
        column_keywords: Optional keywords passed to column header
        row: Shorthand for rows (optional) which are faceted
        row_title: Title text for rows displayed 
        row_sort: Optional sorting for rows
        row_labels: Whether header labels should be displayed
        row_keywords: Optional keywords passed to row header
        aggregate: Aggregation function for y values
        points: Whether to show points
        lines: Whether to show lines
        errorbars: Whether to show errorbars
        error_extent: Extent of errorbars, e.g., stdev or stderr
        limits: Limits for y-axis
        independent_x: Whether x-axes are independent
        independent_y: Whether y-axes are independent
        log_y: Whether y-axes should be log-scale
        y_axis: Axis for y
        spacing: Spacing between facets
        color: Colorscale
        shape: Shape encoding
        detail: Detail encoding
        height: Height of plot in facet
        width: Width of plot in facet

    Returns:
        Chart
    """
    if color is None:
        color_kwarg = {}
    else:
        color_kwarg = {"color": color}

    if shape is None:
        shape_kwarg = {}
    else:
        shape_kwarg = {"shape": shape}

    if detail is None:
        detail_kwarg = {}
    else:
        detail_kwarg = {"detail": detail}

    y_scale_kwarg = {"zero": False}
    if log_y:
        y_scale_kwarg["type"] = "log"
        y_scale_kwarg["base"] = 10
    if limits is not None:
        y_scale_kwarg["domain"] = limits

    y_kwarg = {}
    y_kwarg["scale"] = alt.Scale(**y_scale_kwarg)

    if y_axis is not None:
        y_kwarg["axis"] = y_axis

    lines_layer = (
        alt.Chart()
        .mark_line()
        .encode(
            x=alt.X(x, title=""),
            y=alt.Y(y, aggregate=aggregate, **y_kwarg),
            **color_kwarg,
            **shape_kwarg,
            **detail_kwarg,
        )
    )

    points_layer = (
        alt.Chart()
        .mark_point(filled=True)
        .encode(
            x=alt.X(x, title=""),
            y=alt.Y(y, aggregate=aggregate, **y_kwarg),
            **color_kwarg,
            **shape_kwarg,
            **detail_kwarg,
        )
    )

    errorbars_layer = (
        alt.Chart()
        .mark_errorbar(extent=error_extent)
        .encode(
            x=alt.X(x, title=""),
            y=alt.Y(y, **y_kwarg),
            **color_kwarg,
            **shape_kwarg,
            **detail_kwarg,
        )
    )

    layers = []
    if lines:
        layers.append(lines_layer)
    if points:
        layers.append(points_layer)
    if errorbars:
        layers.append(errorbars_layer)

    chart = alt.layer(*layers, data=df)

    if height is not None:
        chart = chart.properties(height=height)

    if width is not None:
        chart = chart.properties(width=width)

    if column is not None or row is not None:
        facet_kwargs = {
            "spacing": spacing,
        }
        if column is not None:
            facet_kwargs["column"] = alt.Column(
                column,
                title=column_title,
                header=alt.Header(labels=column_labels, **column_keywords),
                sort=column_sort,
            )
        if row is not None:
            facet_kwargs["row"] = alt.Row(
                row,
                title=row_title,
                header=alt.Header(labels=row_labels, **row_keywords),
                sort=row_sort,
            )
        chart = chart.facet(**facet_kwargs)

    if independent_x:
        chart = chart.resolve_scale(x="independent")

    if independent_y:
        chart = chart.resolve_scale(y="independent")

    chart = chart.configure_header(titleOrient=title_orient, labelOrient=label_orient)

    return chart
