from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_special_chars_string(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf53Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf53Tbl",
                 "--item", '{"pk":{"S":"sp"},"v":{"S":"a b/c-d_e"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf53Tbl", Key={"pk": {"S": "sp"}})
    assert resp["Item"]["v"]["S"] == "a b/c-d_e"
