from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_idempotent_then_get(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfIdem",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "delete-item", "--table-name", "WfIdem",
                 "--key", '{"pk":{"S":"ghost"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfIdem", Key={"pk": {"S": "ghost"}})
    assert "Item" not in resp
    result = cli("dynamodb", "put-item", "--table-name", "WfIdem",
                 "--item", '{"pk":{"S":"ghost"},"live":{"BOOL":true}}')
    assert result.returncode == 0
    from _ddb_http import from_item
    resp2 = ddb_client.get_item(TableName="WfIdem", Key={"pk": {"S": "ghost"}})
    assert from_item(resp2["Item"])["live"] is True
