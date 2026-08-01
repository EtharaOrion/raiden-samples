from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_boolean_attribute_roundtrip(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_bool1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_bool1",
                 "--item", '{"pk":{"S":"b1"},"flag":{"BOOL":true}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_bool1", Key={"pk": {"S": "b1"}})
    assert from_item(resp["Item"]) == {"pk": "b1", "flag": True}
