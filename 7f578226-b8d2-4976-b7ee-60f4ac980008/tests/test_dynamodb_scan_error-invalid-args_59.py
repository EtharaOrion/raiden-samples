from _ddb_http import to_item, from_item, to_av, from_av


def test_scan_nonexistent_table_returns_error(cli, ddb_client):
    table_name = "NoSuchScanTable"
    assert table_name not in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "scan", "--table-name", table_name)

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr