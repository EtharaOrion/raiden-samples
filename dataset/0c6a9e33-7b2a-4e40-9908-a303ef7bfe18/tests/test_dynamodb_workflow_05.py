from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_get(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfUpdTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfUpdTbl", Item={"pk": {"S": "a"}})
    result = cli("dynamodb", "update-item", "--table-name", "WfUpdTbl",
                 "--key", '{"pk":{"S":"a"}}',
                 "--update-expression", "SET #s = :v",
                 "--expression-attribute-names", '{"#s":"status"}',
                 "--expression-attribute-values", '{":v":{"S":"active"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfUpdTbl", Key={"pk": {"S": "a"}}, ConsistentRead=True)
    assert from_item(resp["Item"])["status"] == "active"
