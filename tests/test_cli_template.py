from click.testing import CliRunner

from aoc.cli import cli
from aoc.cli_commands import template as template_cli


def test_template_lifecycle(monkeypatch, tmp_path):
	"""
	Tests the full lifecycle of a template: save, list, load, and delete.
	"""
	runner = CliRunner()

	# 1. Arrange: Create a fake project environment in a temporary directory
	fake_templates_dir = tmp_path / ".templates"
	fake_templates_dir.mkdir()
	fake_notepad_path = tmp_path / "notepad.py"
	template_content = "# This is my custom template"
	fake_notepad_path.write_text(template_content)

	# Monkeypatch the path constants in the template command module
	monkeypatch.setattr(template_cli, "TEMPLATES_DIR", fake_templates_dir)
	monkeypatch.setattr(template_cli, "NOTEPAD_PATH", fake_notepad_path)

	# 2. Act & Assert: Save the template
	result_save = runner.invoke(cli, ["template", "save", "my-template"])
	assert result_save.exit_code == 0
	assert "Template 'my-template' saved successfully" in result_save.output
	saved_template_file = fake_templates_dir / "my-template.py.template"
	assert saved_template_file.exists()
	assert saved_template_file.read_text() == template_content

	# 3. Act & Assert: List the templates
	result_list = runner.invoke(cli, ["template", "list"])
	assert result_list.exit_code == 0
	assert "my-template" in result_list.output

	# 4. Act & Assert: Load the template
	# First, change the notepad content to something else
	fake_notepad_path.write_text("# Different content")
	assert fake_notepad_path.read_text() != template_content
	# Now, load the template back, automatically answering "y" to the overwrite prompt
	result_load = runner.invoke(cli, ["template", "load", "my-template"], input="y\n")
	assert result_load.exit_code == 0
	assert "Template 'my-template' loaded" in result_load.output
	assert fake_notepad_path.read_text() == template_content

	# 5. Act & Assert: Delete the template
	# Automatically answer "y" to the confirmation prompt
	result_delete = runner.invoke(
		cli, ["template", "delete", "my-template"], input="y\n"
	)
	assert result_delete.exit_code == 0
	assert "Template 'my-template' deleted" in result_delete.output
	assert not saved_template_file.exists()
