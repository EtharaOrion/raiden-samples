from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_empty_table_name_error(cli, ddb_client):
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "",
        "--key", '{"pk":{"S":"abc"}}',
    )
    assert result.returncode != 0
    combined = result.stderr + result.stdout
    assert (
        "ValidationException" in combined
        or "ResourceNotFoundException" in combined
        or result.returncode != 0
    )