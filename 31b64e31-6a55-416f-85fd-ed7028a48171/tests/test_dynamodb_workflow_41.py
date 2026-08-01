from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_updates_field_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf42Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf42Tbl",
                 "--item", '{"pk":{"S":"u"},"a":{"S":"1"},"b":{"S":"2"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf42Tbl",
                 "--item", '{"pk":{"S":"u"},"a":{"S":"9"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf42Tbl", Key={"pk": {"S": "u"}})
    assert from_item(resp["Item"]) == {"pk": "u", "a": "9"}
