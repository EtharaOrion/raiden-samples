from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_deep_list_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf70Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf70Tbl",
                 "--item", '{"pk":{"S":"dl"},"l":{"L":[{"N":"1"},{"L":[{"S":"nested"}]}]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf70Tbl", Key={"pk": {"S": "dl"}})
    assert from_item(resp["Item"]) == {"pk": "dl", "l": [1, ["nested"]]}
