from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_nonexistent_table_errors(cli, ddb_client):
    long_table_name = "x" * 500
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", long_table_name,
        "--key", '{"pk":{"S":"abc"}}',
    )
    assert result.returncode != 0
    assert (
        "ValidationException" in result.stderr
        or "ResourceNotFoundException" in result.stderr
    )