from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_then_query_subset(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf34Table",
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
    for pk, sk in [("g1", "a"), ("g1", "b"), ("g2", "c")]:
        result = cli("dynamodb", "put-item", "--table-name", "Wf34Table",
                     "--item", '{"pk":{"S":"%s"},"sk":{"S":"%s"}}' % (pk, sk))
        assert result.returncode == 0
    resp = ddb_client.query(
        TableName="Wf34Table",
        KeyConditionExpression="pk = :p",
        ExpressionAttributeValues={":p": {"S": "g1"}},
    )
    got = set(from_item(it)["sk"] for it in resp["Items"])
    assert got == {"a", "b"}
