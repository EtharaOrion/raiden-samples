from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_conditional_fail(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfUpdCond",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfUpdCond",
                 "--item", '{"pk":{"S":"c2"},"v":{"S":"orig"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "WfUpdCond",
                 "--key", '{"pk":{"S":"c2"}}',
                 "--update-expression", "SET v = :v",
                 "--expression-attribute-values", '{":v":{"S":"changed"},":e":{"S":"missing"}}',
                 "--condition-expression", "v = :e")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="WfUpdCond", Key={"pk": {"S": "c2"}})
    assert from_item(resp["Item"])["v"] == "orig"
