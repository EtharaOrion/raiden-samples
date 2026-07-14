from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deleteitem_idempotent(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="TblIdem1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "TblIdem1",
                 "--item", '{"pk":{"S":"present"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "delete-item", "--table-name", "TblIdem1",
                 "--key", '{"pk":{"S":"missing"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="TblIdem1", Key={"pk": {"S": "missing"}})
    assert "Item" not in resp
    assert "Item" in ddb_client.get_item(TableName="TblIdem1", Key={"pk": {"S": "present"}})
