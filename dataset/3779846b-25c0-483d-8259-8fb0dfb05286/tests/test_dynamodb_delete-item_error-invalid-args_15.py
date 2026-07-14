from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_nonexistent_table_error(cli, ddb_client):
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "NoSuchTable12345",
        "--key", '{"pk":{"S":"abc"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr