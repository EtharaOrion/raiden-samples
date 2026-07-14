from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition(cli, ddb_client):
    table_name = "QueryErrTable"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table_name,
        Item={"pk": {"S": "a"}, "v": {"N": "1"}},
    )

    long_name = "x" * 512
    result = cli("dynamodb", "query", "--table-name", long_name)

    assert result.returncode != 0
    assert "ValidationException" in result.stderr

    resp = ddb_client.get_item(TableName=table_name, Key={"pk": {"S": "a"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["v"]["N"] == "1"