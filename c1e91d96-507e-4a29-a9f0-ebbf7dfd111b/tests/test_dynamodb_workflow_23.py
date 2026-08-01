from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_after_overwrite_removes_attr(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfRem1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfRem1",
                 "--item", '{"pk":{"S":"r"},"a":{"S":"1"},"b":{"S":"2"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfRem1",
                 "--item", '{"pk":{"S":"r"},"a":{"S":"1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfRem1", Key={"pk": {"S": "r"}})
    got = from_item(resp["Item"])
    assert got == {"pk": "r", "a": "1"}
    assert "b" not in got
