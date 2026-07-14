from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_nonexistent_table_errors(cli, ddb_client):
    # Do NOT create the table; updating an item on a missing table must fail.
    missing_table = "NoSuchTableForUpdate"
    assert missing_table not in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "update-item",
        "--table-name", missing_table,
        "--key", '{"pk":{"S":"item1"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

    # Verify no table was created as a side effect.
    assert missing_table not in ddb_client.list_tables()["TableNames"]