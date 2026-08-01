from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deep_nested_map_list(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_deep1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_deep1",
                 "--item",
                 '{"pk":{"S":"d1"},"tree":{"M":{"child":{"M":{"leaf":{"L":[{"S":"a"},{"N":"9"}]}}}}}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_deep1", Key={"pk": {"S": "d1"}})
    assert from_item(resp["Item"]) == {
        "pk": "d1", "tree": {"child": {"leaf": ["a", 9]}}}
