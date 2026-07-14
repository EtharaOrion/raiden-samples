from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_failed_condition_keeps_item(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblDelCond1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblDelCond1",
                        Item={"pk": {"S": "dc1"}, "n": {"N": "5"}})
    result = cli("dynamodb", "delete-item", "--table-name", "WfTblDelCond1",
                 "--key", '{"pk":{"S":"dc1"}}',
                 "--condition-expression", "n = :v",
                 "--expression-attribute-values", '{":v":{"N":"99"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfTblDelCond1", Key={"pk": {"S": "dc1"}})
    assert "Item" in resp
