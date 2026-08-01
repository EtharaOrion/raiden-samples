from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_present_after_seed(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf51Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    r1 = cli(
        "dynamodb", "update-item", "--table-name", "Wf51Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"N":"100"}}',
    )
    assert r1.returncode == 0
    r2 = cli(
        "dynamodb", "get-item", "--table-name", "Wf51Tbl",
        "--key", '{"pk":{"S":"a"}}',
    )
    assert r2.returncode == 0
    resp = ddb_client.get_item(TableName="Wf51Tbl", Key={"pk": {"S": "a"}})
    assert "Item" in resp
