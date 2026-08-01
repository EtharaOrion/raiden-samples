from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_get_special_chars(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_spec1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_spec1",
                 "--item", '{"pk":{"S":"sp1"},"txt":{"S":"a/b c:d_e"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_spec1", Key={"pk": {"S": "sp1"}})
    assert from_item(resp["Item"]) == {"pk": "sp1", "txt": "a/b c:d_e"}
