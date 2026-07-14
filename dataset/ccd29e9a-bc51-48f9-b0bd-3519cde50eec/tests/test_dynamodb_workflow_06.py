from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_condition_fail_no_mutation(ddb_client, cli, tmp_path):
    ddb_client.create_table(
        TableName="WfCond1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WfCond1", Item={"pk": {"S": "k"}, "v": {"S": "keep"}})
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "WfCond1",
        "--key", '{"pk":{"S":"k"}}',
        "--update-expression", "SET v = :new",
        "--condition-expression", "v = :expected",
        "--expression-attribute-values", '{":new":{"S":"changed"},":expected":{"S":"wrong"}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfCond1", Key={"pk": {"S": "k"}})
    assert resp["Item"]["v"]["S"] == "keep"
