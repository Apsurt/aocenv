import logging
from pathlib import Path

import click

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
NOTEPAD_PATH = PROJECT_ROOT / "notepad.py"
TEMPLATES_DIR = PROJECT_ROOT / ".templates"


@click.group(name="template")
def template_group():
	"""Manages custom user templates."""
	pass


@template_group.command(name="save")
@click.argument("name")
@click.option(
	"-f", "--force", is_flag=True, help="Force overwrite of an existing template."
)
def template_save(name, force):
	"""Saves the current content of notepad.py as a new template."""
	logger = logging.getLogger(__name__)
	template_path = TEMPLATES_DIR / f"{name}.py.template"

	if template_path.exists() and not force:
		click.secho(
			f"Error: Template '{name}' already exists. Use --force to overwrite.",
			fg="red",
		)
		return

	try:
		content = NOTEPAD_PATH.read_text()
		template_path.write_text(content)
		click.secho(f"✅ Template '{name}' saved successfully.", fg="green")
	except Exception as e:
		logger.error(f"Failed to save template: {e}")


@template_group.command(name="load")
@click.argument("name")
@click.option(
	"-f", "--force", is_flag=True, help="Force overwrite of notepad.py if not empty."
)
def template_load(name, force):
	"""Loads a template into notepad.py."""
	logger = logging.getLogger(__name__)
	template_path = TEMPLATES_DIR / f"{name}.py.template"

	if not template_path.exists():
		click.secho(f"Error: Template '{name}' not found.", fg="red")
		return

	if NOTEPAD_PATH.exists() and NOTEPAD_PATH.read_text().strip() and not force:
		click.secho("Warning: notepad.py is not empty!", fg="yellow")
		if not click.confirm("Do you want to overwrite its contents?"):
			click.echo("Load operation cancelled.")
			return

	try:
		content = template_path.read_text()
		NOTEPAD_PATH.write_text(content)
		click.secho(f"✅ Template '{name}' loaded into notepad.py.", fg="green")
	except Exception as e:
		logger.error(f"Failed to load template: {e}")


@template_group.command(name="list")
def template_list():
	"""Lists all available custom templates."""
	if not TEMPLATES_DIR.exists() or not any(TEMPLATES_DIR.iterdir()):
		click.echo("No custom templates found.")
		return

	click.secho("--- Custom Templates ---", bold=True)
	for template_file in sorted(TEMPLATES_DIR.glob("*.py.template")):
		click.echo(f"  - {template_file.stem.replace('.py', '')}")


@template_group.command(name="delete")
@click.argument("name")
def template_delete(name):
	"""Deletes a saved template."""
	if name.lower() == "default":
		click.secho("Error: The 'default' template is protected.", fg="red")
		return

	template_path = TEMPLATES_DIR / f"{name}.py.template"

	if not template_path.exists():
		click.secho(f"Error: Template '{name}' not found.", fg="red")
		return

	if click.confirm(f"Are you sure you want to delete the template '{name}'?"):
		try:
			template_path.unlink()
			click.secho(f"✅ Template '{name}' deleted.", fg="green")
		except Exception as e:
			logging.getLogger(__name__).error(f"Failed to delete template: {e}")
	else:
		click.echo("Delete operation cancelled.")
