from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_get_unicode_value(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf68Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf68Tbl",
                 "--item", '{"pk":{"S":"u"},"v":{"S":"cafe latte"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf68Tbl", Key={"pk": {"S": "u"}})
    assert resp["Item"]["v"]["S"] == "cafe latte"
