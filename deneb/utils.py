import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import altair as alt
import flatlatex
import numpy as np
import pandas as pd

Chart = alt.vegalite.v4.api.Chart


def display_img(img: str) -> None:
    """Display image inside notebook while preventing browser caching

    Args:
        img: Path to image
    """
    import IPython.display as IPd

    IPd.display(IPd.HTML('<img src="{}?now={}" / >'.format(img, time.time())))


def rgb2hex(r: int, g: int, b: int) -> str:
    """Convert RGB to HEX"""
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def hex2rgb(hex: str) -> Tuple[int]:
    """Convert HEX to RGB"""
    h = hex.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def convert_file(
    fn: str,
    to: str = "png",
    dpi: int = 300,
    background: Optional[str] = None,
    debug: bool = False,
) -> str:
    """Convert files with Inkscape

    Assumes that Inkscape can be called from shell with `inkscape`.

    Args:
        fn: Filename
        to: Target format
        dpi: Resolution
        background: Background color for `--export-background`
        debug: Debug mode

    Returns:
        New filename
    """
    fn = Path(fn).absolute()
    fn_new = fn.with_suffix(f".{to}")

    cmd = f"inkscape --export-filename={str(fn_new)} {str(fn)} --export-dpi={dpi}"

    if background is not None:
        cmd += " --export-background='{background}'"

    if debug:
        print(cmd)
    else:
        cmd += " &> /dev/null"

    subprocess.call(cmd, shell=True)

    return fn_new


def save(
    chart: Chart,
    path: str,
    extra_formats: Optional[Union[str, List[str]]] = None,
    debug: bool = False,
):
    """Save chart using `altair_saver`

    `altair_saver` seems to work best with `.svg` exports. When `extra_formats` is
    specified, the saved file (e.g., a `svg`) can be converted using the `convert_file`
    function which uses `inkscape` for file conversion (e.g., to save `png` or `pdf`
    versions of a chart).

    Args:
        chart: Chart to save
        path: Path to save chart to.
        extra_formats: Extra formats to save chart as, uses `convert_file` on saved file
    """
    try:
        import altair_saver
    except ImportError:
        print("altair_saver is required")
        print("http://github.com/altair-viz/altair_saver/")
        quit()

    path = str(path)
    chart.save(path)

    if extra_formats is not None:
        formats = (
            [extra_formats] if not isinstance(extra_formats, list) else extra_formats
        )
        for ff in formats:
            convert_file(path, to=ff, debug=debug)


def latex2unicode(latex: Union[str, List[str]]) -> Union[str, List[str]]:
    """Converts latex strings to unicode using `flatlatex`

    Args:
        latex: Latex strings (single string or list of strings)

    Returns:
        Unicode strings
    """
    c = flatlatex.converter()
    if type(latex) == str:
        return c.convert(latex)
    elif type(latex) == list:
        return [c.convert(entry) for entry in latex]
    else:
        raise NotImplementedError


def np2df(
    samples: Union[np.ndarray, List[np.ndarray]],
    field: str = "samples",
    labels_samples: Optional[Union[str, List[str]]] = None,
    labels_dim: List[str] = None,
    drop_dim: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Converts numpy arrays to pandas DataFrame used for plotting with `deneb.pairplot`

    Args:
        samples: Samples
        field: Field for sample identifier
        labels_samples: Labels for samples
        labels_dim: Labels for dimensions
        drop_dim: Dimensions to drop

    Returns:
        Formatted pandas DataFrame
    """
    if not isinstance(samples, list):
        samples = [samples]
    samples = [s for s in samples]
    dim_samples = samples[0].shape[1]
    for sample in samples:
        assert sample.shape[1] == dim_samples

    if labels_samples is None:
        labels_samples = [f"sample {i+1}" for i in range(len(samples))]
    if not isinstance(labels_samples, list):
        labels_samples = [labels_samples]
    assert len(labels_samples) == len(samples)

    if labels_dim is None:
        labels_dim = [f"dim {i+1}" for i in range(dim_samples)]
    assert len(labels_dim) == dim_samples

    dfs = []
    for i, sample in enumerate(samples):
        df = pd.DataFrame(sample, columns=labels_dim)
        df[field] = labels_samples[i]
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)

    if drop_dim is not None:
        df = df.drop(columns=drop_dim)
        labels_dim = [ld for ld in labels_dim if ld not in drop_dim]

    return df


def colorscale(
    colors: Dict[str, str], shorthand: str = "sample:N", legend: bool = False,
) -> alt.Color:
    """Build colorscale

    Args:
        colors: Dictionary with domain as keys and range as values
        shorthand: Shorthand for color field
        legend: Whether to show a legend

    Returns:
        Colorscale
    """
    color_params = {
        "scale": alt.Scale(
            domain=[k for k in colors.keys()], range=[v for v in colors.values()]
        ),
    }

    if legend is False:
        color_params["legend"] = None
    else:
        color_params["legend"] = alt.Legend(title=None, orient="right", columns=1)

    colorscale = alt.Color(shorthand, **color_params)

    return colorscale
