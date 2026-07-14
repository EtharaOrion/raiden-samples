from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_conditional_fail(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfPutCond",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfPutCond",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"orig"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfPutCond",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"new"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="WfPutCond", Key={"pk": {"S": "c1"}})
    assert from_item(resp["Item"])["v"] == "orig"
