from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_expression(cli, ddb_client):
    table_name = "QueryErrTbl"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table_name,
        Item={"pk": {"S": "abc"}, "n": {"N": "5"}},
    )

    result = cli("dynamodb", "query", "--table-name", table_name)

    assert result.returncode != 0
    assert "ValidationException" in result.stderr

    resp = ddb_client.query(
        TableName=table_name,
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "abc"}},
    )
    assert resp["Count"] == 1