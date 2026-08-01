from _ddb_http import to_item, from_item, to_av, from_av


def test_create_table_duplicate_name_raises(cli, ddb_client):
    ddb_client.create_table(
        TableName="DupTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert "DupTbl" in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "create-table",
        "--table-name", "DupTbl",
        "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
        "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
        "--provisioned-throughput", '{"ReadCapacityUnits":5,"WriteCapacityUnits":5}',
    )
    assert result.returncode != 0
    assert "ResourceInUseException" in result.stderr

    assert "DupTbl" in ddb_client.list_tables()["TableNames"]