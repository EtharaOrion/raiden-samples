from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multi_item_update_one(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf68Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    for k in ["m1", "m2"]:
        result = cli("dynamodb", "put-item", "--table-name", "Wf68Table",
                     "--item", '{"pk":{"S":"%s"},"v":{"N":"0"}}' % k)
        assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf68Table",
                 "--key", '{"pk":{"S":"m1"}}',
                 "--update-expression", "SET v = :v",
                 "--expression-attribute-values", '{":v":{"N":"9"}}')
    assert result.returncode == 0
    r1 = ddb_client.get_item(TableName="Wf68Table", Key={"pk": {"S": "m1"}})
    r2 = ddb_client.get_item(TableName="Wf68Table", Key={"pk": {"S": "m2"}})
    assert from_item(r1["Item"])["v"] == 9
    assert from_item(r2["Item"])["v"] == 0
