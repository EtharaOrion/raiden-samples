from _ddb_http import to_item, from_item, to_av, from_av


def test_scan_nonexistent_table_raises_resource_not_found(cli, ddb_client):
    result = cli("dynamodb", "scan", "--table-name", "NoSuchTable123")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr