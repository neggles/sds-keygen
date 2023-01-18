from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from sds_keygen import __version__
from sds_keygen.console import console
from sds_keygen.keygen import ModelId, Options, generate_key
from sds_keygen.templates import keyfile

app = typer.Typer()
OPTS = Options()


def version_cb(value: bool):
    if value:
        console.print(f"{__package__} v{__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_cb, is_eager=True, is_flag=True, help="Show version"
    ),
):
    del version
    return


@app.command()
def gen(
    ctx: typer.Context,
    save: bool = typer.Option(
        False,
        "--save",
        "-s",
        help="Save generated keys to file",
        is_flag=True,
    ),
    model_id: ModelId = typer.Option(
        ...,
        "--model",
        "-m",
        help="Model ID (from 'MD5_PR?' SCIP command)",
        show_default=False,
    ),
    device_id: str = typer.Option(
        ...,
        "--id",
        "-i",
        help="Device ID (from 'MD5_SRLN?' SCIP command)",
        show_default=False,
    ),
    outfile: Optional[Path] = typer.Argument(
        None,
        help="Path to save generated keys to (default: ./keys-<model>-<id>.md)",
        show_default=False,
    ),
):
    """
    Generate keys for a particular device ID
    """
    if ctx.resilient_parsing:
        return

    # Remove dashes from scope ID
    device_id = device_id.replace("-", "")
    console.print(f"Generating keys for device ID {device_id}")

    # Set output file name if not specified
    if outfile is not None:
        save = True
    elif save:
        outfile = Path(f"keys-{model_id}-{device_id}.md")

    if save:
        console.print(f"Saving to file: {outfile}")

    key_table = Table(
        title=f"Keys for scope ID {device_id}",
        title_style="bold",
        box=box.ROUNDED,
    )
    key_table.add_column("Group", style="cyan")
    key_table.add_column("Name", style="green")
    key_table.add_column("Code", style="magenta")
    key_table.add_column("Key", style="red")

    last_group = None
    for option in OPTS.All:
        if option.group != last_group:
            key_table.add_section()
            last_group = option.group
        key = generate_key(model_id, device_id, option.code)
        key_table.add_row(option.group, option.name, option.code, key)

    console.print("")
    console.print(key_table)

    if save:
        keyfile_text = keyfile.safe_substitute(
            model_id=model_id.value,
            device_id=device_id,
            key_table=table_to_markdown(key_table).plain,
            package=__package__,
            version=__version__,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        outfile.write_text(keyfile_text)

    console.print("Done!")
    raise typer.Exit()


def table_to_markdown(table: Table):
    # Temporarily remove table title and box styling
    box_temp = table.box
    title_temp = table.title
    table.box = box.MARKDOWN
    table.title = None
    # Capture table as markdown
    capcon = Console(width=120)
    with capcon.capture() as capture:
        capcon.print(table)
    # Restore table title and box styling
    table.box = box_temp
    table.title = title_temp
    # Return captured table as rich.Text
    return Text.from_ansi(capture.get())
