from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_get_missing_key(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_mk1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_mk1",
                 "--item", '{"pk":{"S":"present"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_mk1", Key={"pk": {"S": "absent"}})
    assert "Item" not in resp
    resp2 = ddb_client.get_item(TableName="Tbl_mk1", Key={"pk": {"S": "present"}})
    assert "Item" in resp2
