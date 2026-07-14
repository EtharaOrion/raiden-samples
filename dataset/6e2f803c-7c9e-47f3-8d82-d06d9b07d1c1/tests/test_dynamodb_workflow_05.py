from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_item_then_get_reflects_change(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblUpd1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblUpd1", Item={"pk": {"S": "a1"}})
    result = cli("dynamodb", "update-item", "--table-name", "WfTblUpd1",
                 "--key", '{"pk":{"S":"a1"}}',
                 "--update-expression", "SET #s = :v",
                 "--expression-attribute-names", '{"#s":"Status"}',
                 "--expression-attribute-values", '{":v":{"S":"active"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTblUpd1", Key={"pk": {"S": "a1"}})
    from _ddb_http import from_item
    assert from_item(resp["Item"])["Status"] == "active"
