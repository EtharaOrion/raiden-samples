from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_list_attribute_roundtrip(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_list1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_list1",
                 "--item", '{"pk":{"S":"l1"},"tags":{"L":[{"S":"a"},{"S":"b"}]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_list1", Key={"pk": {"S": "l1"}})
    assert from_item(resp["Item"]) == {"pk": "l1", "tags": ["a", "b"]}
