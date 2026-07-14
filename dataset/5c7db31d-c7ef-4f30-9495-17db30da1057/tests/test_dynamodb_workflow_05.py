from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_then_get_absent(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblE",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblE", Item={"pk": {"S": "row1"}, "v": {"S": "x"}})
    result = cli("dynamodb", "delete-item", "--table-name", "WfTblE",
                 "--key", '{"pk":{"S":"row1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTblE", Key={"pk": {"S": "row1"}})
    assert "Item" not in resp
