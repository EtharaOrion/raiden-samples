from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_nonexistent_idempotent(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf_DelIdem",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "delete-item", "--table-name", "Wf_DelIdem",
                 "--key", '{"pk":{"S":"ghost"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf_DelIdem", Key={"pk": {"S": "ghost"}})
    assert "Item" not in resp
