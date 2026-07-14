from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_item_condition_fail_no_mutation(cli, ddb_client):
    ddb_client.create_table(
        TableName="WFCondUpd",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WFCondUpd", Item={"pk": {"S": "c1"}, "v": {"N": "1"}})
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "WFCondUpd",
        "--key", '{"pk":{"S":"c1"}}',
        "--update-expression", "SET v = :new",
        "--condition-expression", "v = :expected",
        "--expression-attribute-values", '{":new":{"N":"99"},":expected":{"N":"5"}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="WFCondUpd", Key={"pk": {"S": "c1"}}, ConsistentRead=True)
    assert from_item(resp["Item"])["v"] == 1
