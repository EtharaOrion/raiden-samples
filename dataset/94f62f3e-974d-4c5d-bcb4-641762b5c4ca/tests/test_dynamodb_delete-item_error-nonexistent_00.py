from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_nonexistent_table(cli, ddb_client):
    assert "NoSuchTable" not in ddb_client.list_tables()["TableNames"]
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "NoSuchTable",
        "--key", '{"pk":{"S":"abc"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr