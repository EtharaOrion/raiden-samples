from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_updates_accumulate(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf30Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    r1 = cli(
        "dynamodb", "update-item", "--table-name", "Wf30Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET a = :a",
        "--expression-attribute-values", '{":a":{"S":"1"}}',
    )
    assert r1.returncode == 0
    r2 = cli(
        "dynamodb", "update-item", "--table-name", "Wf30Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET b = :b",
        "--expression-attribute-values", '{":b":{"S":"2"}}',
    )
    assert r2.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf30Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["a"] == "1" and item["b"] == "2"
