from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_nested_map_in_list(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfNest1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfNest1",
                 "--item", '{"pk":{"S":"nst"},"docs":{"L":[{"M":{"id":{"N":"1"}}},{"M":{"id":{"N":"2"}}}]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfNest1", Key={"pk": {"S": "nst"}})
    got = from_item(resp["Item"])
    assert got["docs"] == [{"id": 1}, {"id": 2}]
