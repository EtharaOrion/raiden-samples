from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_empty_string_attr(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl34",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl34",
                 "--item", '{"pk":{"S":"es1"},"note":{"S":""}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl34", Key={"pk": {"S": "es1"}})
    assert resp["Item"]["note"]["S"] == ""
