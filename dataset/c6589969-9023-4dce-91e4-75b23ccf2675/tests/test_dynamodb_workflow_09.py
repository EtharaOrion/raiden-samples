from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_conditional_no_mutate(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfUpdCond",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfUpdCond",
                 "--item", '{"pk":{"S":"u1"},"v":{"S":"keep"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "WfUpdCond",
                 "--key", '{"pk":{"S":"u1"}}',
                 "--update-expression", "SET v = :new",
                 "--expression-attribute-values", '{":new":{"S":"changed"},":chk":{"S":"nope"}}',
                 "--condition-expression", "v = :chk")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfUpdCond", Key={"pk": {"S": "u1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["v"] == "keep"
