from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deleteitem_condition_fails(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(TableName="WfTblDelCond1",
                            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
                            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
                            BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblDelCond1", Item={"pk": {"S": "k1"}, "v": {"N": "1"}})
    result = cli("dynamodb", "delete-item", "--table-name", "WfTblDelCond1",
                 "--key", '{"pk":{"S":"k1"}}',
                 "--condition-expression", "v = :bad",
                 "--expression-attribute-values", '{":bad":{"N":"999"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfTblDelCond1", Key={"pk": {"S": "k1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["v"] == 1
