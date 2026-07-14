from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_then_query_empty(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf12Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf12Tbl",
                 "--item", '{"pk":{"S":"z1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf12Tbl",
                 "--item", '{"pk":{"S":"z2"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf12Tbl",
                 "--key", '{"pk":{"S":"z1"}}')
    assert result.returncode == 0
    resp = ddb_client.query(
        TableName="Wf12Tbl",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "z1"}},
    )
    assert resp["Items"] == []
    resp2 = ddb_client.get_item(TableName="Wf12Tbl", Key={"pk": {"S": "z2"}})
    assert "Item" in resp2
