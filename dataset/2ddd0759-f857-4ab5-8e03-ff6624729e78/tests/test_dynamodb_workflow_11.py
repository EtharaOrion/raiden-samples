from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_idempotent(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfIdem1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "delete-item", "--table-name", "WfIdem1",
                 "--key", '{"pk":{"S":"ghost"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfIdem1", Key={"pk": {"S": "ghost"}})
    assert "Item" not in resp
    result = cli("dynamodb", "put-item", "--table-name", "WfIdem1",
                 "--item", '{"pk":{"S":"ghost"},"v":{"S":"now"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="WfIdem1", Key={"pk": {"S": "ghost"}})
