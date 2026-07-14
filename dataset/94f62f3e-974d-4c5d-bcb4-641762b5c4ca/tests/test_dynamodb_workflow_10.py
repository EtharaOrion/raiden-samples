from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deleteitem_condition_fail_keeps_item(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf_DelCond1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf_DelCond1", Item={"pk": {"S": "dc1"}, "v": {"N": "5"}})
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "Wf_DelCond1",
        "--key", '{"pk":{"S":"dc1"}}',
        "--condition-expression", "v = :expected",
        "--expression-attribute-values", '{":expected":{"N":"999"}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf_DelCond1", Key={"pk": {"S": "dc1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["v"] == 5
