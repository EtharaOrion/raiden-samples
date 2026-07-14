from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seeding(ddb_client, cli, tmp_path):
    ddb_client.create_table(
        TableName="WfQuery1",
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
    ddb_client.put_item(TableName="WfQuery1", Item={"pk": {"S": "p"}, "sk": {"S": "s1"}})
    ddb_client.put_item(TableName="WfQuery1", Item={"pk": {"S": "p"}, "sk": {"S": "s2"}})
    ddb_client.put_item(TableName="WfQuery1", Item={"pk": {"S": "q"}, "sk": {"S": "s3"}})
    result = cli(
        "dynamodb", "query",
        "--table-name", "WfQuery1",
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", '{":v":{"S":"p"}}',
    )
    assert result.returncode == 0
    items = ddb_client.query(
        TableName="WfQuery1",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "p"}},
    )["Items"]
    sks = {it["sk"]["S"] for it in items}
    assert sks == {"s1", "s2"}
