from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_nonexistent_idempotent(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WFDelIdem",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "delete-item", "--table-name", "WFDelIdem",
                 "--key", '{"pk":{"S":"ghost"}}')
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName="WFDelIdem", Key={"pk": {"S": "ghost"}})
    assert "Item" not in resp

    result = cli("dynamodb", "put-item", "--table-name", "WFDelIdem",
                 "--item", '{"pk":{"S":"real"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WFDelIdem", Key={"pk": {"S": "real"}})
    assert "Item" in resp
