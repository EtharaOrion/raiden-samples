from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_missing_table_errors(cli, ddb_client):
    missing_table = "NoSuchTablePutItem"
    assert missing_table not in ddb_client.list_tables()["TableNames"]
    result = cli(
        "dynamodb",
        "put-item",
        "--table-name",
        missing_table,
        "--item",
        '{"pk":{"S":"abc"},"n":{"N":"5"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert missing_table not in ddb_client.list_tables()["TableNames"]