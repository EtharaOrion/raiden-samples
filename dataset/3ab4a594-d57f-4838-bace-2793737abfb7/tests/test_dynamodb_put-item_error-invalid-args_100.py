from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_nonexistent_table_errors(cli, ddb_client):
    # No table created; PutItem against a missing table must fail.
    table_name = "MissingTable"
    assert table_name not in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "put-item",
        "--table-name", table_name,
        "--item", '{"pk":{"S":"abc"},"n":{"N":"5"}}',
    )

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

    # Table still absent; nothing was created as a side effect.
    assert table_name not in ddb_client.list_tables()["TableNames"]