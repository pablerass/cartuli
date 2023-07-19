import pytest

from pathlib import Path

from cartuli.__main__ import parse_args


def test_args():
    assert parse_args([]).definition_file == Path("Cartulifile.yml")
    assert parse_args(['Cf.yml']).definition_file == Path("Cf.yml")
    with pytest.raises(SystemExit):
        parse_args(['Cf1.yml', 'Cf2.yml'])
