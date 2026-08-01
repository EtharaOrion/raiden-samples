from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_wrong_key_type_absent(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_gwkt1",
                 "--attribute-definitions", '[{"AttributeName":"id","AttributeType":"N"}]',
                 "--key-schema", '[{"AttributeName":"id","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_gwkt1",
                 "--item", '{"id":{"N":"5"},"v":{"S":"five"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_gwkt1", Key={"id": {"N": "6"}})
    assert "Item" not in resp
    resp2 = ddb_client.get_item(TableName="Tbl_gwkt1", Key={"id": {"N": "5"}})
    assert from_item(resp2["Item"]) == {"id": 5, "v": "five"}
