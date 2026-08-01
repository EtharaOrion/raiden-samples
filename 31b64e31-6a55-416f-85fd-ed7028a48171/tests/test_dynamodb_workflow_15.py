from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_map_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf16Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf16Tbl",
                 "--item", '{"pk":{"S":"m1"},"m":{"M":{"k":{"S":"v"}}}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf16Tbl", Key={"pk": {"S": "m1"}})
    assert from_item(resp["Item"]) == {"pk": "m1", "m": {"k": "v"}}
