from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_and_readback_via_list_and_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf71Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "Wf71Tbl" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "put-item", "--table-name", "Wf71Tbl",
                 "--item", '{"pk":{"S":"rb"},"v":{"S":"read"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Wf71Tbl",
                 "--key", '{"pk":{"S":"rb"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf71Tbl", Key={"pk": {"S": "rb"}})
    assert from_item(resp["Item"]) == {"pk": "rb", "v": "read"}
