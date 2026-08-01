from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_describe_then_put_then_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfDpg1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "describe-table", "--table-name", "WfDpg1")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfDpg1",
                 "--item", '{"pk":{"S":"dpg"},"count":{"N":"3"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "WfDpg1",
                 "--key", '{"pk":{"S":"dpg"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfDpg1", Key={"pk": {"S": "dpg"}})
    assert from_item(resp["Item"]) == {"pk": "dpg", "count": 3}
