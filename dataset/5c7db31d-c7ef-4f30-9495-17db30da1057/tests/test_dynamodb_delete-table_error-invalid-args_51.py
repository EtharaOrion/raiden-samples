from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_table_nonexistent_returns_resource_not_found(cli, ddb_client):
    assert "GhostTable" not in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", "GhostTable")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr