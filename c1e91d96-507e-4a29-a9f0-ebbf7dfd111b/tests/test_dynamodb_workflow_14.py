from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_bool_and_null(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfBool1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfBool1",
                 "--item", '{"pk":{"S":"b"},"flag":{"BOOL":true},"empty":{"NULL":true}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfBool1", Key={"pk": {"S": "b"}})
    got = from_item(resp["Item"])
    assert got["flag"] is True
    assert got["empty"] is None
