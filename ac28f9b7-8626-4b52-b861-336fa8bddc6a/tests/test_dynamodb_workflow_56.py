from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_five_query_all(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf57Table",
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
    skeys = ["s0", "s1", "s2", "s3", "s4"]
    for sk in skeys:
        result = cli("dynamodb", "put-item", "--table-name", "Wf57Table",
                     "--item", '{"pk":{"S":"h"},"sk":{"S":"%s"}}' % sk)
        assert result.returncode == 0
    resp = ddb_client.query(
        TableName="Wf57Table",
        KeyConditionExpression="pk = :p",
        ExpressionAttributeValues={":p": {"S": "h"}},
    )
    got = set(from_item(it)["sk"] for it in resp["Items"])
    assert got == set(skeys)
