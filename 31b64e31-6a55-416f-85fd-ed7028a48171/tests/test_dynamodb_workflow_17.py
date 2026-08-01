from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_then_absent_key_then_put(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf18Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Wf18Tbl",
                 "--key", '{"pk":{"S":"later"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf18Tbl", Key={"pk": {"S": "later"}})
    assert "Item" not in resp
    result = cli("dynamodb", "put-item", "--table-name", "Wf18Tbl",
                 "--item", '{"pk":{"S":"later"},"v":{"S":"now"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf18Tbl", Key={"pk": {"S": "later"}})
    assert from_item(resp["Item"]) == {"pk": "later", "v": "now"}
