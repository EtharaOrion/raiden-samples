from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_conditional_no_mutation(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(
        TableName="WfUpdCond1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfUpdCond1",
                 "--item", '{"pk":{"S":"u1"},"v":{"N":"10"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "WfUpdCond1",
                 "--key", '{"pk":{"S":"u1"}}',
                 "--update-expression", "SET v = :new",
                 "--condition-expression", "v = :expected",
                 "--expression-attribute-values", '{":new":{"N":"99"},":expected":{"N":"5"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfUpdCond1", Key={"pk": {"S": "u1"}})
    assert from_item(resp["Item"])["v"] == 10
