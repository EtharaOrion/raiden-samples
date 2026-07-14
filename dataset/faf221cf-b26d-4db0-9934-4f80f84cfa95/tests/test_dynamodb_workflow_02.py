from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import from_item


def test_workflow_put_delete_get(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfDel1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfDel1",
                 "--item", '{"pk":{"S":"d1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "WfDel1",
                 "--key", '{"pk":{"S":"d1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfDel1", Key={"pk": {"S": "d1"}})
    assert "Item" not in resp
