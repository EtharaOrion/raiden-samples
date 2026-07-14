from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_updateitem_then_getitem_reflects(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(TableName="WfTblUpd1",
                            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
                            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
                            BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblUpd1", Item={"pk": {"S": "u1"}, "Status": {"S": "old"}})
    result = cli("dynamodb", "update-item", "--table-name", "WfTblUpd1",
                 "--key", '{"pk":{"S":"u1"}}',
                 "--update-expression", "SET #s = :v",
                 "--expression-attribute-names", '{"#s":"Status"}',
                 "--expression-attribute-values", '{":v":{"S":"active"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTblUpd1", Key={"pk": {"S": "u1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["Status"] == "active"
