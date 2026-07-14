from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_then_get_absent(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WFDeleteGet",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "WFDeleteGet",
                 "--item", '{"pk":{"S":"d1"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "delete-item", "--table-name", "WFDeleteGet",
                 "--key", '{"pk":{"S":"d1"}}')
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName="WFDeleteGet", Key={"pk": {"S": "d1"}})
    assert "Item" not in resp
