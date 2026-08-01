from _ddb_http import to_item, from_item, to_av, from_av


def test_scan_table_name_too_long_validation(cli, ddb_client):
    long_name = "x" * 512
    result = cli("dynamodb", "scan", "--table-name", long_name)
    assert result.returncode != 0
    assert "ValidationException" in result.stderr or "ResourceNotFoundException" in result.stderr