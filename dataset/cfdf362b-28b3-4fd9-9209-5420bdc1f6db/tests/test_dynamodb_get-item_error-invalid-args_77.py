from _ddb_http import to_item, from_item, to_av, from_av


def test_get_item_missing_table_returns_error(cli, ddb_client):
    result = cli(
        "dynamodb",
        "get-item",
        "--table-name",
        "NonExistentTable",
        "--key",
        '{"pk":{"S":"abc"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "NonExistentTable" not in ddb_client.list_tables()["TableNames"]