from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_deleteitem_getitem(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="TblDelItem1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "TblDelItem1",
                 "--item", '{"pk":{"S":"k1"},"v":{"S":"hello"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="TblDelItem1", Key={"pk": {"S": "k1"}})

    result = cli("dynamodb", "delete-item", "--table-name", "TblDelItem1",
                 "--key", '{"pk":{"S":"k1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="TblDelItem1", Key={"pk": {"S": "k1"}})
    assert "Item" not in resp
