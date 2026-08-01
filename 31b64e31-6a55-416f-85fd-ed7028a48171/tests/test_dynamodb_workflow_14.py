from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_list_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf15Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf15Tbl",
                 "--item", '{"pk":{"S":"l1"},"items":{"L":[{"S":"x"},{"S":"y"}]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf15Tbl", Key={"pk": {"S": "l1"}})
    assert from_item(resp["Item"]) == {"pk": "l1", "items": ["x", "y"]}
