import altair as alt

from deneb.__version__ import __version__
from .correlation_matrix import correlation_matrix
from .lineplot import lineplot
from .pairplot import pairplot
from .themes import get_style, set_style
from .utils import (
    colorscale,
    convert_file,
    display_img,
    hex2rgb,
    latex2unicode,
    np2df,
    rgb2hex,
    save,
)

__all__ = [
    convert_file,
    colorscale,
    correlation_matrix,
    display_img,
    get_style,
    hex2rgb,
    latex2unicode,
    np2df,
    pairplot,
    rgb2hex,
    save,
    set_style,
]
