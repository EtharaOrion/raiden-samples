from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_nonexistent_item_idempotent(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    table = "WfDelIdem"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", table,
                 "--item", '{"pk":{"S":"keep"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", table,
                 "--key", '{"pk":{"S":"ghost"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "keep"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["pk"] == "keep"
    ghost = ddb_client.get_item(TableName=table, Key={"pk": {"S": "ghost"}})
    assert "Item" not in ghost
