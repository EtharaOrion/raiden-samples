from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_after_delete_recreate(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf32Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf32Tbl", Item={"pk": {"S": "a"}, "v": {"S": "old"}})
    result = cli("dynamodb", "delete-table", "--table-name", "Wf32Tbl")
    assert result.returncode == 0
    ddb_client.create_table(
        TableName="Wf32Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    resp = ddb_client.get_item(TableName="Wf32Tbl", Key={"pk": {"S": "a"}})
    assert "Item" not in resp
