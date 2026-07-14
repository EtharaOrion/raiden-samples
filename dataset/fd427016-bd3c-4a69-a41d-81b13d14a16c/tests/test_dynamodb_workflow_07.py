from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_conditional_fail(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(
        TableName="WfTblDelCond",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfTblDelCond",
                 "--item", '{"pk":{"S":"d1"},"v":{"S":"keep"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "WfTblDelCond",
                 "--key", '{"pk":{"S":"d1"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfTblDelCond", Key={"pk": {"S": "d1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["v"] == "keep"
