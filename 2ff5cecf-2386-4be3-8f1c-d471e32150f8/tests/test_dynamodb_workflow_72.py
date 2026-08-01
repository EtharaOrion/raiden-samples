from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_two_keys_isolated(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf73Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    r1 = cli(
        "dynamodb", "update-item", "--table-name", "Wf73Tbl",
        "--key", '{"pk":{"S":"k1"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"S":"one"}}',
    )
    assert r1.returncode == 0
    r2 = cli(
        "dynamodb", "update-item", "--table-name", "Wf73Tbl",
        "--key", '{"pk":{"S":"k2"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"S":"two"}}',
    )
    assert r2.returncode == 0
    i1 = from_item(ddb_client.get_item(TableName="Wf73Tbl", Key={"pk": {"S": "k1"}})["Item"])
    i2 = from_item(ddb_client.get_item(TableName="Wf73Tbl", Key={"pk": {"S": "k2"}})["Item"])
    assert i1["v"] == "one" and i2["v"] == "two"
