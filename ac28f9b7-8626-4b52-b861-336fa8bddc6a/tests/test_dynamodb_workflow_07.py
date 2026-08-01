from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_multiple_query(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf8Table",
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
    for sk in ["s1", "s2", "s3"]:
        result = cli("dynamodb", "put-item", "--table-name", "Wf8Table",
                     "--item", '{"pk":{"S":"grp"},"sk":{"S":"%s"}}' % sk)
        assert result.returncode == 0
    resp = ddb_client.query(
        TableName="Wf8Table",
        KeyConditionExpression="pk = :p",
        ExpressionAttributeValues={":p": {"S": "grp"}},
    )
    got = set(from_item(it)["sk"] for it in resp["Items"])
    assert got == {"s1", "s2", "s3"}
