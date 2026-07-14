from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_table_name_too_long(cli, ddb_client):
    long_name = "x" * 300
    item = '{"pk":{"S":"abc"},"n":{"N":"5"}}'
    result = cli("dynamodb", "put-item", "--table-name", long_name, "--item", item)
    assert result.returncode != 0
    assert "ValidationException" in result.stderr or "ResourceNotFoundException" in result.stderr