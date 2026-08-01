from _ddb_http import to_item, from_item, to_av, from_av


def test_get_item_nonexistent_table(cli, ddb_client):
    missing_table = "x" * 300
    result = cli(
        "dynamodb", "get-item",
        "--table-name", missing_table,
        "--key", '{"pk":{"S":"abc"}}',
    )
    assert result.returncode != 0
    assert (
        "ValidationException" in result.stderr
        or "ResourceNotFoundException" in result.stderr
    )
    assert missing_table not in ddb_client.list_tables()["TableNames"]