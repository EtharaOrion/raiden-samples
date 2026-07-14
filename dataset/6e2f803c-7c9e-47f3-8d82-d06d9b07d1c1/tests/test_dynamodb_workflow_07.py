from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_item_failed_condition_no_mutate(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblUpdCond1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblUpdCond1",
                        Item={"pk": {"S": "c1"}, "n": {"N": "1"}})
    result = cli("dynamodb", "update-item", "--table-name", "WfTblUpdCond1",
                 "--key", '{"pk":{"S":"c1"}}',
                 "--update-expression", "SET n = :new",
                 "--condition-expression", "n = :expected",
                 "--expression-attribute-values",
                 '{":new":{"N":"99"},":expected":{"N":"42"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="WfTblUpdCond1", Key={"pk": {"S": "c1"}})
    assert from_item(resp["Item"])["n"] == 1
