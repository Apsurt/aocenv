from click.testing import CliRunner
from aoc.cli import hello

def test_hello_cli():
    runner = CliRunner()
    result = runner.invoke(hello)
    assert result.exit_code == 0
    assert "Hello from aocenv!" in result.output
