from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_wrong_key_after_put(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf29Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf29Tbl",
                 "--item", '{"pk":{"S":"exists"},"v":{"S":"here"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf29Tbl", Key={"pk": {"S": "other"}})
    assert "Item" not in resp
    resp = ddb_client.get_item(TableName="Wf29Tbl", Key={"pk": {"S": "exists"}})
    assert from_item(resp["Item"]) == {"pk": "exists", "v": "here"}
