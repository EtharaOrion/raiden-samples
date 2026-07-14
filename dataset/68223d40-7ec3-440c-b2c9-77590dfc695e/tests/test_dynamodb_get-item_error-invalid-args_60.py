from _ddb_http import to_item, from_item, to_av, from_av


def test_get_item_nonexistent_table_returns_error(cli, ddb_client):
    long_table_name = "x" * 500
    key_json = '{"pk":{"S":"abc"}}'
    result = cli(
        "dynamodb", "get-item",
        "--table-name", long_table_name,
        "--key", key_json,
    )
    assert result.returncode != 0
    assert (
        "ValidationException" in result.stderr
        or "ResourceNotFoundException" in result.stderr
    )