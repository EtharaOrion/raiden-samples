from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deleteitem_idempotent(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfIdem",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfIdem",
                 "--item", '{"pk":{"S":"present"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "WfIdem",
                 "--key", '{"pk":{"S":"absent"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfIdem", Key={"pk": {"S": "present"}})
    assert "Item" in resp
