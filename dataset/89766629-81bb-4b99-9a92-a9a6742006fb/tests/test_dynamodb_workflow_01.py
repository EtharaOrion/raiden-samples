from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_deleteitem_gone(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfDelItem",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfDelItem",
                 "--item", '{"pk":{"S":"gone"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "WfDelItem",
                 "--key", '{"pk":{"S":"gone"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfDelItem", Key={"pk": {"S": "gone"}})
    assert "Item" not in resp
