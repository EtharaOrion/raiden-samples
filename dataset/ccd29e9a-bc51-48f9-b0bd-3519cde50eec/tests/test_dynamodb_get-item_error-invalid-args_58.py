from _ddb_http import to_item, from_item, to_av, from_av


def test_get_item_nonexistent_table(cli, ddb_client):
    result = cli(
        "dynamodb", "get-item",
        "--table-name", "NoSuchTableXYZ",
        "--key", '{"pk":{"S":"abc"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "NoSuchTableXYZ" not in ddb_client.list_tables()["TableNames"]