from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_put_list_get_full(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf27Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "Wf27Tbl" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "put-item", "--table-name", "Wf27Tbl",
                 "--item", '{"pk":{"S":"full"},"a":{"S":"1"},"b":{"N":"2"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Wf27Tbl",
                 "--key", '{"pk":{"S":"full"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf27Tbl", Key={"pk": {"S": "full"}})
    assert from_item(resp["Item"]) == {"pk": "full", "a": "1", "b": 2}
