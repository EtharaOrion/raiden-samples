from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_delete_get_gone(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="DelTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")

    result = cli("dynamodb", "put-item", "--table-name", "DelTbl",
                 "--item", '{"pk":{"S":"d1"},"v":{"S":"x"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="DelTbl", Key={"pk": {"S": "d1"}})

    result = cli("dynamodb", "delete-item", "--table-name", "DelTbl",
                 "--key", '{"pk":{"S":"d1"}}')
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName="DelTbl", Key={"pk": {"S": "d1"}})
    assert "Item" not in resp
