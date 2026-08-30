"""Locked marimo lesson exported to a self-hosted WASM application."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", app_title="Information after hard labels")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
        # Information after hard labels

        A hard label replaces each score by the mean score of its cell. Move the
        bin slider and watch how much of the original one-parameter Fisher
        information that conditional expectation retains.

        This lesson runs entirely in your browser. It is locked to the curated
        calculation: there is no arbitrary-code editor in the first portal release.
        """
    )
    return


@app.cell
def _(mo):
    bin_control = mo.ui.slider(2, 10, value=4, step=1, label="Number of hard bins")
    bin_control
    return (bin_control,)


@app.cell
def _(bin_control):
    import numpy as np

    score_grid = np.linspace(-3.5, 3.5, 241)
    score_weights = np.exp(-0.5 * score_grid**2)
    score_weights /= score_weights.sum()
    ordered_groups = np.array_split(np.arange(score_grid.size), bin_control.value)
    cell_means = np.array(
        [np.average(score_grid[group], weights=score_weights[group]) for group in ordered_groups]
    )
    cell_weights = np.array([score_weights[group].sum() for group in ordered_groups])
    information_full = float(np.sum(score_weights * score_grid**2))
    information_binned = float(np.sum(cell_weights * cell_means**2))
    retention = information_binned / information_full
    return cell_means, information_binned, information_full, retention, score_grid


@app.cell
def _(bin_control, cell_means, mo, retention, score_grid):
    width = 760
    height = 210
    x_coordinates = 36 + (score_grid + 3.5) / 7 * (width - 72)
    point_markup = "".join(
        f'<circle cx="{x:.2f}" cy="130" r="2.2" fill="#276be8" opacity=".58" />'
        for x in x_coordinates[::3]
    )
    center_markup = "".join(
        f'<circle cx="{36 + (center + 3.5) / 7 * (width - 72):.2f}" cy="96" r="7" '
        'fill="#07142d" stroke="#20bfae" stroke-width="3" />'
        for center in cell_means
    )
    chart = f"""
    <svg viewBox="0 0 {width} {height}" role="img" aria-label="One-dimensional score cells">
      <rect width="{width}" height="{height}" rx="8" fill="#07142d" />
      <line x1="36" y1="130" x2="{width - 36}" y2="130" stroke="#6d829d" />
      {point_markup}{center_markup}
      <text x="36" y="178" fill="#91a4bd" font-family="monospace" font-size="12">−3.5</text>
      <text x="{width - 64}" y="178" fill="#91a4bd"
            font-family="monospace" font-size="12">+3.5</text>
    </svg>
    """
    mo.vstack(
        [
            mo.Html(chart),
            mo.callout(
                mo.md(
                    f"**{bin_control.value} bins retain {retention * 100:.2f}%** of the "
                    "discretized Gaussian location information. The cyan rings are the "
                    "conditional score means that replace every event in their cell."
                ),
                kind="info",
            ),
        ]
    )
    return


@app.cell
def _(information_binned, information_full, mo):
    mo.md(
        rf"""
        The calculation is the one-dimensional form of the exact identity

        \[
        I_q = \sum_b W_b \mu_b^2,
        \qquad I_{{\mathrm{{full}}}} - I_q =
        \mathbb{{E}}[\operatorname{{Var}}(S\mid q(S))].
        \]

        Here, \(I_{{\mathrm{{full}}}}={information_full:.6f}\) and
        \(I_q={information_binned:.6f}\). The gap is an accountable within-cell
        variance—not a visual heuristic.
        """
    )
    return


if __name__ == "__main__":
    app.run()
