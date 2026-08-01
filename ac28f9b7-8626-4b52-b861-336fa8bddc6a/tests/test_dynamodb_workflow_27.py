from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_update(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf28Table",
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
    result = cli("dynamodb", "put-item", "--table-name", "Wf28Table",
                 "--item", '{"pk":{"S":"g"},"sk":{"S":"a"},"score":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf28Table",
                 "--key", '{"pk":{"S":"g"},"sk":{"S":"a"}}',
                 "--update-expression", "SET score = :s",
                 "--expression-attribute-values", '{":s":{"N":"100"}}')
    assert result.returncode == 0
    resp = ddb_client.query(
        TableName="Wf28Table",
        KeyConditionExpression="pk = :p",
        ExpressionAttributeValues={":p": {"S": "g"}},
    )
    scores = [from_item(it)["score"] for it in resp["Items"]]
    assert scores == [100]
