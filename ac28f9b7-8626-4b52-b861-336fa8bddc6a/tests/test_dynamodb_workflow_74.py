from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_query_after_remove(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf75Table",
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
    for sk in ["a", "b"]:
        result = cli("dynamodb", "put-item", "--table-name", "Wf75Table",
                     "--item", '{"pk":{"S":"g"},"sk":{"S":"%s"},"extra":{"S":"e"}}' % sk)
        assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf75Table",
                 "--key", '{"pk":{"S":"g"},"sk":{"S":"a"}}',
                 "--update-expression", "REMOVE extra")
    assert result.returncode == 0
    resp = ddb_client.query(
        TableName="Wf75Table",
        KeyConditionExpression="pk = :p",
        ExpressionAttributeValues={":p": {"S": "g"}},
    )
    by_sk = {from_item(it)["sk"]: from_item(it) for it in resp["Items"]}
    assert "extra" not in by_sk["a"] and by_sk["b"]["extra"] == "e"
