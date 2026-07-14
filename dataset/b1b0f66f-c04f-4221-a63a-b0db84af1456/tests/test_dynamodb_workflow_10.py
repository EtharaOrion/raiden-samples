from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_condition_fail(cli, ddb_client):
    ddb_client.create_table(
        TableName="WFCondDel",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WFCondDel", Item={"pk": {"S": "d1"}, "v": {"N": "3"}})
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "WFCondDel",
        "--key", '{"pk":{"S":"d1"}}',
        "--condition-expression", "v = :expected",
        "--expression-attribute-values", '{":expected":{"N":"7"}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WFCondDel", Key={"pk": {"S": "d1"}}, ConsistentRead=True)
    assert "Item" in resp
