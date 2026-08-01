from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_describe_then_put(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl4",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "describe-table", "--table-name", "WfTbl4")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl4",
                 "--item", '{"pk":{"S":"k1"},"v":{"S":"hello"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl4", Key={"pk": {"S": "k1"}})
    assert resp["Item"]["v"]["S"] == "hello"
