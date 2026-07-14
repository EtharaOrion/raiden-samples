from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_conditional_fails(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(
        TableName="WfTblDelCond",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfTblDelCond",
                 "--item", '{"pk":{"S":"dc1"},"v":{"S":"live"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "WfTblDelCond",
                 "--key", '{"pk":{"S":"dc1"}}',
                 "--condition-expression", "v = :x",
                 "--expression-attribute-values", '{":x":{"S":"nomatch"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfTblDelCond", Key={"pk": {"S": "dc1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["v"] == "live"
