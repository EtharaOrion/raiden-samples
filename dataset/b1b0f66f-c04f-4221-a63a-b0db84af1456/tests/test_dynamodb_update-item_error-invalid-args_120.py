from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_nonexistent_table_error(cli, ddb_client):
    # Attempt to update an item in a table that does not exist.
    table_name = "NoSuchTableForUpdate"
    assert table_name not in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "update-item",
        "--table-name", table_name,
        "--key", '{"pk":{"S":"abc"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

    # Table still absent - no side effect occurred.
    assert table_name not in ddb_client.list_tables()["TableNames"]