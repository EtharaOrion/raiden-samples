from _ddb_http import to_item, from_item, to_av, from_av


def test_get_item_nonexistent_table_error(cli, ddb_client):
    result = cli(
        "dynamodb",
        "get-item",
        "--table-name",
        "x" * 600,
        "--key",
        '{"pk":{"S":"abc"}}',
    )
    assert result.returncode != 0
    assert (
        "ValidationException" in result.stderr
        or "ResourceNotFoundException" in result.stderr
    )