from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_delete_get_absent(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "DelTbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "DelTbl",
                 "--item", '{"pk":{"S":"k1"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="DelTbl", Key={"pk": {"S": "k1"}})

    result = cli("dynamodb", "delete-item", "--table-name", "DelTbl",
                 "--key", '{"pk":{"S":"k1"}}')
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName="DelTbl", Key={"pk": {"S": "k1"}})
    assert "Item" not in resp
