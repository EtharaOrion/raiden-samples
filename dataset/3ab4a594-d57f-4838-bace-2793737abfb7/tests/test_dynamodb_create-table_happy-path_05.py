from _ddb_http import to_item, from_item, to_av, from_av


def test_create_table_creates_new_table(cli, ddb_client):
    result = cli(
        "dynamodb", "create-table",
        "--table-name", "Tbl1",
        "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
        "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
        "--provisioned-throughput", '{"ReadCapacityUnits":5,"WriteCapacityUnits":5}',
    )
    assert result.returncode == 0
    assert "Tbl1" in ddb_client.list_tables()["TableNames"]