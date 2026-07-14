from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_condition_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfDelCond",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfDelCond",
                 "--item", '{"pk":{"S":"dc1"},"v":{"S":"present"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "WfDelCond",
                 "--key", '{"pk":{"S":"dc1"}}',
                 "--condition-expression", "v = :x",
                 "--expression-attribute-values", '{":x":{"S":"wrong"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfDelCond", Key={"pk": {"S": "dc1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["v"] == "present"
