from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_and_count_query(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf51Table",
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
    for i in range(4):
        result = cli("dynamodb", "put-item", "--table-name", "Wf51Table",
                     "--item", '{"pk":{"S":"grp"},"sk":{"N":"%d"}}' % i)
        assert result.returncode == 0
    resp = ddb_client.query(
        TableName="Wf51Table",
        KeyConditionExpression="pk = :p",
        ExpressionAttributeValues={":p": {"S": "grp"}},
    )
    assert len(resp["Items"]) == 4
