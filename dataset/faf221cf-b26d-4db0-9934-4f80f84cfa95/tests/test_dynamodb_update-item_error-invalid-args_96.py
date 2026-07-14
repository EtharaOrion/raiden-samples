from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_missing_update_on_nonexistent_table(cli, ddb_client):
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "NoSuchTable",
        "--key", '{"pk":{"S":"abc"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr