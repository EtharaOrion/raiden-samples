from _ddb_http import to_item, from_item, to_av, from_av


def test_create_table_duplicate_name_conflict(cli, ddb_client):
    table_name = "DupTable"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert table_name in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "create-table",
        "--table-name", table_name,
        "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
        "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
        "--provisioned-throughput", '{"ReadCapacityUnits":5,"WriteCapacityUnits":5}',
    )
    assert result.returncode != 0
    assert "ResourceInUseException" in result.stderr