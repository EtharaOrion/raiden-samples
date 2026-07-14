from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deleteitem_nonexistent_idempotent(cli, ddb_client, tmp_path):
    ddb_client.create_table(TableName="WfTblDelIdem1",
                            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
                            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
                            BillingMode="PAY_PER_REQUEST")
    result = cli("dynamodb", "delete-item", "--table-name", "WfTblDelIdem1",
                 "--key", '{"pk":{"S":"ghost"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTblDelIdem1", Key={"pk": {"S": "ghost"}})
    assert "Item" not in resp
