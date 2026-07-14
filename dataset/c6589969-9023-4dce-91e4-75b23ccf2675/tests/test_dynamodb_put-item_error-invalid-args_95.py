from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_nonexistent_table_errors(cli, ddb_client):
    # Do NOT create the table; put-item must fail against a missing table.
    result = cli(
        "dynamodb",
        "put-item",
        "--table-name",
        "NoSuchTable",
        "--item",
        '{"pk":{"S":"abc"},"n":{"N":"5"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    # Verify no table was created as a side effect.
    assert "NoSuchTable" not in ddb_client.list_tables()["TableNames"]