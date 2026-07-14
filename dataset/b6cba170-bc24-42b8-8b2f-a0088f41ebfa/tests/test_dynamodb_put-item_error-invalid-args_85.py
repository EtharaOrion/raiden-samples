from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_empty_table_name(cli, ddb_client):
    result = cli(
        "dynamodb", "put-item",
        "--table-name", "",
        "--item", '{"pk":{"S":"abc"},"n":{"N":"5"}}',
    )
    assert result.returncode != 0
    combined = result.stderr + result.stdout
    assert ("ValidationException" in combined) or ("ResourceNotFoundException" in combined) or (result.returncode != 0)
    assert "abc" not in [
        n for n in ddb_client.list_tables()["TableNames"]
    ]