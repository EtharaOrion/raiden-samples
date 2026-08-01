from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_updateitem_failing_condition_no_mutate(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf7Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf7Table",
                 "--item", '{"pk":{"S":"c1"},"v":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf7Table",
                 "--key", '{"pk":{"S":"c1"}}',
                 "--update-expression", "SET v = :new",
                 "--condition-expression", "v = :expected",
                 "--expression-attribute-values", '{":new":{"N":"99"},":expected":{"N":"5"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf7Table", Key={"pk": {"S": "c1"}})
    assert from_item(resp["Item"])["v"] == 1
