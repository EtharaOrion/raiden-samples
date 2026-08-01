from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_then_get_empty_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_cget1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "Tbl_cget1" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "get-item", "--table-name", "Tbl_cget1",
                 "--key", '{"pk":{"S":"anything"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_cget1", Key={"pk": {"S": "anything"}})
    assert "Item" not in resp
