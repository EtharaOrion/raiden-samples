from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_list_item_readback(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl15",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl15",
                 "--item", '{"pk":{"S":"l1"},"items":{"L":[{"S":"a"},{"S":"b"}]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl15", Key={"pk": {"S": "l1"}})
    vals = [e["S"] for e in resp["Item"]["items"]["L"]]
    assert vals == ["a", "b"]
