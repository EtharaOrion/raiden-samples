from _ddb_http import to_item, from_item, to_av, from_av


def test_create_table_missing_required_key_schema(cli, ddb_client):
    long_name = "x" * 300
    result = cli(
        "dynamodb", "create-table",
        "--table-name", long_name,
        "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
        "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
        "--provisioned-throughput", '{"ReadCapacityUnits":5,"WriteCapacityUnits":5}',
    )
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    assert long_name not in ddb_client.list_tables()["TableNames"]