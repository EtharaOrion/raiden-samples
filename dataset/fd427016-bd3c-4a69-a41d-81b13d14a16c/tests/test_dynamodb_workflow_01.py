from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_delete_get_absent(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblB",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfTblB",
                 "--item", '{"pk":{"S":"b1"},"v":{"S":"x"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "WfTblB",
                 "--key", '{"pk":{"S":"b1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTblB", Key={"pk": {"S": "b1"}})
    assert "Item" not in resp
