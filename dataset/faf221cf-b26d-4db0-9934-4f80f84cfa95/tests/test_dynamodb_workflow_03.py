from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import from_item


def test_workflow_delete_nonexistent_idempotent(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfDelIdem1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfDelIdem1",
                 "--item", '{"pk":{"S":"present"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "WfDelIdem1",
                 "--key", '{"pk":{"S":"ghost"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfDelIdem1", Key={"pk": {"S": "present"}})
    assert "Item" in resp
