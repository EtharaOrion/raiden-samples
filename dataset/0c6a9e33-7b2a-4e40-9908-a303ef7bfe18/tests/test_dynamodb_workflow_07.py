from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_condition_fails_no_mutation(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfCondUpd",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfCondUpd", Item={"pk": {"S": "a"}, "n": {"N": "1"}})
    result = cli("dynamodb", "update-item", "--table-name", "WfCondUpd",
                 "--key", '{"pk":{"S":"a"}}',
                 "--update-expression", "SET n = :new",
                 "--condition-expression", "n = :expected",
                 "--expression-attribute-values", '{":new":{"N":"99"},":expected":{"N":"5"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfCondUpd", Key={"pk": {"S": "a"}}, ConsistentRead=True)
    assert from_item(resp["Item"])["n"] == 1
