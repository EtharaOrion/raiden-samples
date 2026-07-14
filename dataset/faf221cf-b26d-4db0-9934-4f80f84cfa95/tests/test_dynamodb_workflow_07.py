from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import from_item


def test_workflow_update_condition_fails_no_mutation(cli, ddb_client, tmp_path):
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
                 "--expression-attribute-values", '{":new":{"N":"20"},":chk":{"N":"999"}}',
                 "--condition-expression", "v = :chk")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfUpdCond1", Key={"pk": {"S": "u1"}})
    assert resp["Item"]["v"] == {"N": "10"}
