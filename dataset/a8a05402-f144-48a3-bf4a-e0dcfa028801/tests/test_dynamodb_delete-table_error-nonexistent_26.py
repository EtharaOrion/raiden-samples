from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_table_nonexistent(cli, ddb_client):
    assert "NoSuchTable" not in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", "NoSuchTable")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr