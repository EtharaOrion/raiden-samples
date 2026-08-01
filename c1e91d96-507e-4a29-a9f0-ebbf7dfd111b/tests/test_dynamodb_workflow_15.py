from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_list_attribute(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfList1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfList1",
                 "--item", '{"pk":{"S":"l"},"items":{"L":[{"S":"a"},{"N":"2"}]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfList1", Key={"pk": {"S": "l"}})
    got = from_item(resp["Item"])
    assert got["items"] == ["a", 2]
