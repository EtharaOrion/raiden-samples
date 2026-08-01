from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_absent_key_no_item(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf7Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Wf7Tbl",
                 "--key", '{"pk":{"S":"nope"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf7Tbl", Key={"pk": {"S": "nope"}})
    assert "Item" not in resp
