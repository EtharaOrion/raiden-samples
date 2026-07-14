from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_multiple_items(cli, ddb_client, tmp_path):
    table = "WfQuery"
    ddb_client.create_table(
        TableName=table,
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
        result = cli("dynamodb", "put-item", "--table-name", table,
                     "--item", '{"pk":{"S":"P"},"sk":{"S":"%s"}}' % sk)
        assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", table,
                 "--item", '{"pk":{"S":"Q"},"sk":{"S":"x"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "query", "--table-name", table,
                 "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"P"}}')
    assert result.returncode == 0
    items = ddb_client.query(
        TableName=table,
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "P"}},
    )["Items"]
    sks = {i["sk"]["S"] for i in items}
    assert sks == {"s1", "s2", "s3"}
