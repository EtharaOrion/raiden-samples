from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_empty_before_put(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfEmp1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "WfEmp1",
                 "--key", '{"pk":{"S":"nope"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfEmp1", Key={"pk": {"S": "nope"}})
    assert "Item" not in resp
    result = cli("dynamodb", "put-item", "--table-name", "WfEmp1",
                 "--item", '{"pk":{"S":"nope"},"now":{"S":"here"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfEmp1", Key={"pk": {"S": "nope"}})
    assert from_item(resp["Item"]) == {"pk": "nope", "now": "here"}
