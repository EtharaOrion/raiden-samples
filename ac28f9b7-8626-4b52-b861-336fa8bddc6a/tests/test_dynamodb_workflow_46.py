from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multiple_partitions_query_each(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf47Table",
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    for pk in ["p1", "p2"]:
        result = cli("dynamodb", "put-item", "--table-name", "Wf47Table",
                     "--item", '{"pk":{"S":"%s"},"sk":{"S":"only"}}' % pk)
        assert result.returncode == 0
    resp = ddb_client.query(
        TableName="Wf47Table",
        KeyConditionExpression="pk = :p",
        ExpressionAttributeValues={":p": {"S": "p2"}},
    )
    got = [from_item(it)["pk"] for it in resp["Items"]]
    assert got == ["p2"]
