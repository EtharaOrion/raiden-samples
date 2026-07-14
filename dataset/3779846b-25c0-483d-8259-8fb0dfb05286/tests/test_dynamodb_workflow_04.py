from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_seed(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfQ1",
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
    ddb_client.put_item(TableName="WfQ1", Item={"pk": {"S": "g"}, "sk": {"S": "1"}})
    ddb_client.put_item(TableName="WfQ1", Item={"pk": {"S": "g"}, "sk": {"S": "2"}})
    ddb_client.put_item(TableName="WfQ1", Item={"pk": {"S": "other"}, "sk": {"S": "9"}})
    result = cli(
        "dynamodb", "query",
        "--table-name", "WfQ1",
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", '{":v":{"S":"g"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.query(
        TableName="WfQ1",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "g"}},
    )
    sks = {from_item(it)["sk"] for it in resp["Items"]}
    assert sks == {"1", "2"}
