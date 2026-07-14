from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_nonexistent_table_errors(cli, ddb_client):
    # Ensure the target table does not exist.
    assert "NoSuchTable" not in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "put-item",
        "--table-name", "NoSuchTable",
        "--item", '{"pk":{"S":"abc"},"n":{"N":"5"}}',
    )

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

    # The table still must not exist as a side effect.
    assert "NoSuchTable" not in ddb_client.list_tables()["TableNames"]