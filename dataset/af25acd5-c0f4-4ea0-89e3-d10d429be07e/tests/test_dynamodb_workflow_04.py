from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_nonexistent_idempotent(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="IdemTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")

    result = cli("dynamodb", "delete-item", "--table-name", "IdemTbl",
                 "--key", '{"pk":{"S":"ghost"}}')
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName="IdemTbl", Key={"pk": {"S": "ghost"}})
    assert "Item" not in resp
