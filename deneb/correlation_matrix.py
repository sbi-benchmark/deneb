from typing import Any, Dict, List, Optional, Tuple, Union

import altair as alt
import pandas as pd

from .utils import Chart


def correlation_matrix(
    df: pd.DataFrame,
    metrics: List[str],
    limits: Optional[Union[Tuple[float], List[float]]] = None,
    font_size: int = 12,
    sparse: bool = True,
    white_font: float = 0.5,
    rotate_outwards: bool = False,
    legend: bool = False,
    height: Optional[int] = None,
    width: Optional[int] = None,
) -> Chart:
    """Correlation matrix

    Args:
        df: Dataframe
        metrics: Metrics to correlate (columns of dataframe)
        limits: Limits
        font_size: Font size for correlations
        sparse: Hides extra fields
        white_font: Threshold correlation for using white instead of black
        rotate_outwards: Rotates labels away from matrix
        legend: Whether or not to show legend
        height: Height of plot in facet
        width: Width of plot in facet

    Returns:
        Chart
    """
    valid_metrics = [m for m in metrics if m in df.columns]
    df_valid = df[valid_metrics]

    corrMatrix = df_valid.corr().reset_index().melt("index")
    corrMatrix.columns = ["var1", "var2", "correlation"]

    axis_params = {
        "domainWidth": 0,
        "tickWidth": 0,
    }

    if not rotate_outwards:
        xaxis = alt.Axis(labelAngle=0.0, **axis_params)
        yaxis = alt.Axis(labelAngle=270.0, **axis_params)
    else:
        xaxis = alt.Axis(labelAngle=270.0, **axis_params)
        yaxis = alt.Axis(labelAngle=0.0, **axis_params)

    color_params = {}
    if legend is False:
        color_params["legend"] = None
    else:
        color_params["legend"] = alt.Legend(title=None, orient="right", columns=1)
    if limits is not None:
        color_params["scale"] = alt.Scale(domain=limits)

    chart = (
        alt.Chart(corrMatrix)
        .mark_rect()
        .encode(
            x=alt.X("var1", title=None, axis=xaxis),
            y=alt.Y("var2", title=None, axis=yaxis),
            color=alt.Color("correlation", **color_params),
        )
    )

    chart += chart.mark_text(size=font_size).encode(
        text=alt.Text("correlation", format=".2f"),
        color=alt.condition(
            f"datum.correlation > {white_font}", alt.value("white"), alt.value("black"),
        ),
    )

    if sparse:
        chart = chart.transform_filter("datum.var1 < datum.var2")

    if height is not None:
        chart = chart.properties(height=height)

    if width is not None:
        chart = chart.properties(width=width)

    return chart
