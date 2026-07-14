from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_getitem_absent_key_no_item(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="TblAbsent1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "TblAbsent1",
                 "--item", '{"pk":{"S":"exists"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "get-item", "--table-name", "TblAbsent1",
                 "--key", '{"pk":{"S":"nope"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="TblAbsent1", Key={"pk": {"S": "nope"}})
    assert "Item" not in resp
    assert "Item" in ddb_client.get_item(TableName="TblAbsent1", Key={"pk": {"S": "exists"}})
