from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_nonexistent_table_errors(cli, ddb_client):
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "NoSuchTableForUpdate",
        "--key", '{"pk":{"S":"abc"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "NoSuchTableForUpdate" not in ddb_client.list_tables()["TableNames"]