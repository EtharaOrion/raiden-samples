from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_updateitem_condition_fails_no_mutation(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(TableName="WfTblUpdCond1",
                            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
                            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
                            BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblUpdCond1", Item={"pk": {"S": "c1"}, "n": {"N": "5"}})
    result = cli("dynamodb", "update-item", "--table-name", "WfTblUpdCond1",
                 "--key", '{"pk":{"S":"c1"}}',
                 "--update-expression", "SET n = :new",
                 "--condition-expression", "n = :expect",
                 "--expression-attribute-values", '{":new":{"N":"77"},":expect":{"N":"999"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfTblUpdCond1", Key={"pk": {"S": "c1"}})
    assert from_item(resp["Item"])["n"] == 5
