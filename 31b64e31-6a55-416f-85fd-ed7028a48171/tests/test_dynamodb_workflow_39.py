from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_get_before_any_put(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf40Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Wf40Tbl",
                 "--key", '{"pk":{"S":"nothing"}}')
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf40Tbl", Key={"pk": {"S": "nothing"}})
