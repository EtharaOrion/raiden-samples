from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_puts_query_multi(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf42Table",
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "N"},
        ],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf42Table",
                 "--item", '{"pk":{"S":"q"},"sk":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf42Table",
                 "--item", '{"pk":{"S":"q"},"sk":{"N":"2"}}')
    assert result.returncode == 0
    resp = ddb_client.query(
        TableName="Wf42Table",
        KeyConditionExpression="pk = :p",
        ExpressionAttributeValues={":p": {"S": "q"}},
    )
    got = set(from_item(it)["sk"] for it in resp["Items"])
    assert got == {1, 2}
