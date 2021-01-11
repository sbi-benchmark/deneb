from functools import partial
from typing import Any, Dict, Optional

import altair as alt
from mergedeep import merge


def get_style() -> Dict[str, Any]:
    """Get current style

    Returns:
        Dictionary with current style
    """
    return alt.themes.get()()


def set_style(
    border: bool = False,
    font_family: Optional[str] = None,
    font_size: Optional[int] = None,
    font_size_label: Optional[int] = None,
    font_size_title: Optional[int] = None,
    font_weight: Optional[str] = "normal",
    font_weight_label: Optional[str] = None,
    font_weight_title: Optional[str] = None,
    google_font: bool = False,
    grid: bool = False,
    height: int = 100,
    width: int = 100,
    extra: Dict[str, Any] = {},
):
    """Set custom style

    Any additional kwargs are merged into the config dict as well

    Args:
        font_family: Font family to use
        font_size: Font size for all labels and titles
        font_size_label: If provided, overrides `font_size` for all labels
        font_size_title: If provided, overrides `font_size` for all titles
        font_weight: Font weight for all labels and titles
        font_weight_label: If provided, overrides `font_weight` for all titles
        font_weight_title: If provided, overrides `font_weight` for all labels
        google_font: Whether to load font from Google Fonts
        grid: Whether to show grid
        border: Whether to show borders
        height: Height
        width: Width
        extra: Any extra config

    Returns:
        None
    """

    theme_font_family = _custom_font_family(font_family)
    theme_font_size_label = _custom_font_size_label(
        font_size if font_size_label is None else font_size_label
    )
    theme_font_size_title = _custom_font_size_title(
        font_size if font_size_title is None else font_size_title
    )
    theme_font_weight_label = _custom_font_weight_label(
        font_weight if font_weight_label is None else font_weight_label
    )
    theme_font_weight_title = _custom_font_weight_title(
        font_weight if font_weight_title is None else font_weight_title
    )
    theme_grid = {"config": {"axis": {"grid": grid}}}
    theme_height = {
        "config": {"view": {"continuousHeight": height, "discreteHeight": height}}
    }
    theme_width = {
        "config": {"view": {"continuousWidth": width, "discreteWidth": width}}
    }
    theme_border = {"config": {"view": {"strokeWidth": 0}}} if not border else {}

    theme = merge(
        {},
        theme_border,
        theme_font_family,
        theme_font_size_label,
        theme_font_size_title,
        theme_font_weight_label,
        theme_font_weight_title,
        theme_grid,
        theme_height,
        theme_width,
        extra,
    )

    def custom_theme():
        return theme

    alt.themes.register("custom_theme", custom_theme)
    alt.themes.enable("custom_theme")

    if google_font and font_family is not None:
        from IPython.core.display import HTML, display

        return display(
            HTML(
                f"<link rel='stylesheet' href='https://fonts.googleapis.com/css?family={font_family}'>"
            )
        )


def _custom_font_family(font_family: Optional[str]) -> Dict[str, Any]:
    if font_family is None:
        return {}
    else:
        return {
            "config": {
                "title": {"font": font_family},
                "axis": {"labelFont": font_family, "titleFont": font_family},
                "header": {"labelFont": font_family, "titleFont": font_family},
                "legend": {"labelFont": font_family, "titleFont": font_family},
            }
        }


def _custom_font_size_title(font_size: Optional[int]) -> Dict[str, Any]:
    if font_size is None:
        return {}
    else:
        return {
            "config": {
                "title": {"fontSize": font_size},
                "axis": {"titleFontSize": font_size},
                "header": {"titleFontSize": font_size},
                "legend": {"titleFontSize": font_size},
            }
        }


def _custom_font_size_label(font_size: Optional[int]) -> Dict[str, Any]:
    if font_size is None:
        return {}
    else:
        return {
            "config": {
                "axis": {"labelFontSize": font_size},
                "header": {"labelFontSize": font_size},
                "legend": {"labelFontSize": font_size},
            }
        }


def _custom_font_weight_title(font_weight: Optional[str]) -> Dict[str, Any]:
    if font_weight is None:
        return {}
    else:
        return {
            "config": {
                "axis": {"titleFontWeight": font_weight},
                "header": {"titleFontWeight": font_weight},
                "legend": {"titleFontWeight": font_weight},
            }
        }


def _custom_font_weight_label(font_weight: Optional[str]) -> Dict[str, Any]:
    if font_weight is None:
        return {}
    else:
        return {
            "config": {
                "axis": {"labelFontWeight": font_weight},
                "header": {"labelFontWeight": font_weight},
                "legend": {"labelFontWeight": font_weight},
            }
        }
