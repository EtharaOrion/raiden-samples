from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deleteitem_condition_fail(ddb_client, cli, tmp_path):
    ddb_client.create_table(
        TableName="WfDelCond1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WfDelCond1", Item={"pk": {"S": "k"}, "v": {"S": "alive"}})
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "WfDelCond1",
        "--key", '{"pk":{"S":"k"}}',
        "--condition-expression", "v = :expected",
        "--expression-attribute-values", '{":expected":{"S":"nope"}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfDelCond1", Key={"pk": {"S": "k"}})
    assert resp["Item"]["v"]["S"] == "alive"
