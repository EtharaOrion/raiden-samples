from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_describe_limits_list_put_update_full(cli, ddb_client):
    result = cli("dynamodb", "describe-limits")
    assert result.returncode == 0
    ddb_client.create_table(
        TableName="Wf80Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "Wf80Table" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "put-item", "--table-name", "Wf80Table",
                 "--item", '{"pk":{"S":"full1"},"v":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf80Table",
                 "--key", '{"pk":{"S":"full1"}}',
                 "--update-expression", "SET v = :v",
                 "--expression-attribute-values", '{":v":{"N":"2"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf80Table", Key={"pk": {"S": "full1"}})
    assert from_item(resp["Item"])["v"] == 2
