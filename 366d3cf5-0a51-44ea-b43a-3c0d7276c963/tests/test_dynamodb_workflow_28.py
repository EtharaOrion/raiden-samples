from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_list_map(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf29",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf29",
                 "--item", '{"pk":{"S":"m"},"lst":{"L":[{"S":"a"},{"N":"1"}]},"mp":{"M":{"x":{"S":"y"}}}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf29", Key={"pk": {"S": "m"}})
    assert from_item(resp["Item"]) == {"pk": "m", "lst": ["a", 1], "mp": {"x": "y"}}
