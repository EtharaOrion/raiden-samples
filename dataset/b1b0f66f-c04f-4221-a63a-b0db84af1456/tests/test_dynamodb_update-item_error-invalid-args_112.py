from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_missing_required_update_against_nonexistent_table(cli, ddb_client):
    long_name = "x" * 300
    result = cli(
        "dynamodb", "update-item",
        "--table-name", long_name,
        "--key", '{"pk":{"S":"abc"}}',
        "--update-expression", "SET n = :v",
        "--expression-attribute-values", '{":v":{"N":"5"}}',
    )
    assert result.returncode != 0
    assert (
        "ValidationException" in result.stderr
        or "ResourceNotFoundException" in result.stderr
    )
    assert long_name not in ddb_client.list_tables()["TableNames"]