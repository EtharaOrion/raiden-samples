from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_nonexistent_table(cli, ddb_client):
    # Ensure the target table does not exist so UpdateItem must fail.
    missing = "NoSuchTable_UpdateItem"
    assert missing not in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "update-item",
        "--table-name", missing,
        "--key", '{"pk":{"S":"abc"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

    # Table still absent - no item collection was created.
    assert missing not in ddb_client.list_tables()["TableNames"]