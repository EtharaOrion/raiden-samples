from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_condition_fail_no_mutation(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf_UpdCond1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf_UpdCond1", Item={"pk": {"S": "c1"}, "v": {"N": "1"}})
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "Wf_UpdCond1",
        "--key", '{"pk":{"S":"c1"}}',
        "--update-expression", "SET v = :new",
        "--condition-expression", "v = :expected",
        "--expression-attribute-values", '{":new":{"N":"99"},":expected":{"N":"7"}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf_UpdCond1", Key={"pk": {"S": "c1"}})
    assert from_item(resp["Item"])["v"] == 1
