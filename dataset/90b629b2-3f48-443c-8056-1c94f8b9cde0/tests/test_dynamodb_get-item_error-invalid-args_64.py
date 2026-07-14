from _ddb_http import to_item, from_item, to_av, from_av


def test_get_item_nonexistent_table_errors(cli, ddb_client):
    # Ensure the target table does not exist.
    missing_table = "NoSuchTable_getitem"
    assert missing_table not in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "get-item",
        "--table-name", missing_table,
        "--key", '{"pk":{"S":"abc"}}',
    )

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr