from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_nonexistent_table_error(cli, ddb_client):
    """put-item against a table that does not exist must fail with a service error."""
    table_name = "MissingTable123"

    # Ensure the target table is absent.
    assert table_name not in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "put-item",
        "--table-name", table_name,
        "--item", '{"pk":{"S":"abc"},"n":{"N":"5"}}',
    )

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

    # The table must still not exist (no side effect created).
    assert table_name not in ddb_client.list_tables()["TableNames"]