from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_nonexistent_table_error(cli, ddb_client):
    # Ensure the target table does not exist.
    table_name = "NoSuchTable_PutItem"
    assert table_name not in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "put-item",
        "--table-name", table_name,
        "--item", '{"pk":{"S":"abc"},"n":{"N":"5"}}',
    )

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

    # Verify no table was created as a side effect.
    assert table_name not in ddb_client.list_tables()["TableNames"]