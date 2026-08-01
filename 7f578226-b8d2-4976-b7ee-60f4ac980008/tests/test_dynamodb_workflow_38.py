from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_null_attr_readback(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl36",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl36",
                 "--item", '{"pk":{"S":"nl1"},"empty":{"NULL":true}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl36", Key={"pk": {"S": "nl1"}})
    assert resp["Item"]["empty"]["NULL"] is True
