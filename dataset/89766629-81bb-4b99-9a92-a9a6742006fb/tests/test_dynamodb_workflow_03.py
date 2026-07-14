from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seed(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(
        TableName="WfQuery",
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
    for sk in ("s1", "s2", "s3"):
        result = cli("dynamodb", "put-item", "--table-name", "WfQuery",
                     "--item", '{"pk":{"S":"P"},"sk":{"S":"' + sk + '"}}')
        assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfQuery",
                 "--item", '{"pk":{"S":"other"},"sk":{"S":"x"}}')
    assert result.returncode == 0
    items = ddb_client.query(
        TableName="WfQuery",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "P"}},
    )["Items"]
    sks = {from_item(it)["sk"] for it in items}
    assert sks == {"s1", "s2", "s3"}
