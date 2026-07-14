from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_conditional_fail_no_mutation(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfUpd2",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WfUpd2", Item={"pk": {"S": "a"}, "v": {"S": "orig"}})
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "WfUpd2",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET v = :new",
        "--condition-expression", "v = :expected",
        "--expression-attribute-values", '{":new":{"S":"changed"},":expected":{"S":"wrong"}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfUpd2", Key={"pk": {"S": "a"}})
    assert from_item(resp["Item"])["v"] == "orig"
