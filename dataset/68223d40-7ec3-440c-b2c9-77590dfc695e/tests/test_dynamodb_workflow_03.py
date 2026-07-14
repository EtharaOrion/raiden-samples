from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_getitem_reflects(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfUpd1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    ddb_client.put_item(TableName="WfUpd1", Item={"pk": {"S": "u1"}, "status": {"S": "old"}})
    result = cli("dynamodb", "update-item", "--table-name", "WfUpd1",
                 "--key", '{"pk":{"S":"u1"}}',
                 "--update-expression", "SET #s = :v",
                 "--expression-attribute-names", '{"#s":"status"}',
                 "--expression-attribute-values", '{":v":{"S":"new"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfUpd1", Key={"pk": {"S": "u1"}})
    assert from_item(resp["Item"])["status"] == "new"
