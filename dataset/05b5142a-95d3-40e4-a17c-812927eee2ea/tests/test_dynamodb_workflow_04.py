from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_idempotent(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfDelIdem",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfDelIdem", Item={"pk": {"S": "keep"}})
    result = cli("dynamodb", "delete-item", "--table-name", "WfDelIdem",
                 "--key", '{"pk":{"S":"nope"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfDelIdem", Key={"pk": {"S": "keep"}})
    assert "Item" in resp
