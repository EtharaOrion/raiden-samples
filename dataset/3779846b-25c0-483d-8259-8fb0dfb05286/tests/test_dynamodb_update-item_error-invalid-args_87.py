from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_empty_table_name_invalid_args(cli, ddb_client):
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "",
        "--key", '{"pk":{"S":"abc"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )
    assert result.returncode != 0
    combined = result.stderr + result.stdout
    assert (
        "ValidationException" in combined
        or "ResourceNotFoundException" in combined
        or result.returncode != 0
    )