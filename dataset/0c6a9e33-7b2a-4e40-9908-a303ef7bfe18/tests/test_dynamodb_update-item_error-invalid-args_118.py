from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_nonexistent_table_resource_not_found(cli, ddb_client):
    # Do NOT create the table; update-item against a missing table must fail.
    missing_table = "NoSuchTableForUpdate"
    assert missing_table not in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "update-item",
        "--table-name", missing_table,
        "--key", '{"pk":{"S":"abc"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

    # Table still absent; no side effect created.
    assert missing_table not in ddb_client.list_tables()["TableNames"]