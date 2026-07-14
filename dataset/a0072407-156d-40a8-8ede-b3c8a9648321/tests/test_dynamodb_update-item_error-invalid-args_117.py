from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_missing_required_update_on_nonexistent_table(cli, ddb_client):
    long_name = "x" * 300
    result = cli(
        "dynamodb", "update-item",
        "--table-name", long_name,
        "--key", '{"pk":{"S":"abc"}}',
        "--update-expression", "SET #a = :v",
        "--expression-attribute-names", '{"#a":"attr"}',
        "--expression-attribute-values", '{":v":{"S":"val"}}',
    )
    assert result.returncode != 0
    assert (
        "ValidationException" in result.stderr
        or "ResourceNotFoundException" in result.stderr
    )