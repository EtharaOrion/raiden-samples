def test_list_keys_invalid_empty_marker(cli, kms):
    result = cli("kms", "list-keys", "--marker", "")
    assert result.returncode != 0
    assert "Marker" in result.stderr or "InvalidMarker" in result.stderr or "ValidationException" in result.stderr