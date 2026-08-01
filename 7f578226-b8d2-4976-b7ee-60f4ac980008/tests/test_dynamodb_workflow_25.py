from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_numeric_key_attribute(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl23",
                 "--attribute-definitions", '[{"AttributeName":"id","AttributeType":"N"}]',
                 "--key-schema", '[{"AttributeName":"id","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl23",
                 "--item", '{"id":{"N":"100"},"v":{"S":"nk"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl23", Key={"id": {"N": "100"}})
    assert resp["Item"]["v"]["S"] == "nk"
