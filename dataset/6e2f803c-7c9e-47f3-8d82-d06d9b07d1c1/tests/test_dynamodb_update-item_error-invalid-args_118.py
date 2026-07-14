from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_nonexistent_table_errors(cli, ddb_client):
    # Ensure the target table does not exist.
    assert "NoSuchTbl" not in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "update-item",
        "--table-name", "NoSuchTbl",
        "--key", '{"pk":{"S":"abc"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

    # Table still absent -> no side effect occurred.
    assert "NoSuchTbl" not in ddb_client.list_tables()["TableNames"]