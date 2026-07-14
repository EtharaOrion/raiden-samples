from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_list_getitem_lifecycle(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfLifecycle1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "WfLifecycle1" in ddb_client.list_tables()["TableNames"]
    ddb_client.put_item(TableName="WfLifecycle1", Item={"pk": {"S": "a1"}, "v": {"N": "7"}})
    result = cli("dynamodb", "get-item", "--table-name", "WfLifecycle1",
                 "--key", '{"pk":{"S":"a1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfLifecycle1", Key={"pk": {"S": "a1"}})
    assert from_item(resp["Item"]) == {"pk": "a1", "v": 7}
