def test_list_aliases_invalid_empty_marker(cli, kms):
    result = cli("kms", "list-aliases", "--marker", "")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Marker" in result.stderr or "Validation" in result.stderr or "Invalid" in result.stderr