from _ddb_http import to_item, from_item, to_av, from_av


def test_describe_table_nonexistent_error(cli, ddb_client):
    table_name = "NonExistentTableXYZ"
    assert table_name not in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "describe-table", "--table-name", table_name)
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr