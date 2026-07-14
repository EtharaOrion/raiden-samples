from _ddb_http import to_item, from_item, to_av, from_av


def test_get_item_nonexistent_table(cli, ddb_client):
    table_name = "NonexistentTable123"
    assert table_name not in ddb_client.list_tables()["TableNames"]
    result = cli(
        "dynamodb", "get-item",
        "--table-name", table_name,
        "--key", '{"pk":{"S":"abc"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr