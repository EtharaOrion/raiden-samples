from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_invalid_oversized_table_name(cli, ddb_client):
    oversized_name = "x" * 300
    result = cli(
        "dynamodb", "put-item",
        "--table-name", oversized_name,
        "--item", '{"pk":{"S":"abc"},"n":{"N":"5"}}',
    )
    assert result.returncode != 0
    assert (
        "ValidationException" in result.stderr
        or "ResourceNotFoundException" in result.stderr
    )
    assert oversized_name not in ddb_client.list_tables()["TableNames"]