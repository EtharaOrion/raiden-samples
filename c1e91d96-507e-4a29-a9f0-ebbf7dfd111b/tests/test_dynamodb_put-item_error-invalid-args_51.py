from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_nonexistent_table_error(cli, ddb_client):
    result = cli(
        "dynamodb", "put-item",
        "--table-name", "NoSuchTable",
        "--item", '{"pk":{"S":"abc"},"n":{"N":"5"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "NoSuchTable" not in ddb_client.list_tables()["TableNames"]