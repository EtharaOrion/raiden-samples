from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_tables_independent_items(cli, ddb_client, tmp_path):
    for nm in ("Wf63A", "Wf63B"):
        ddb_client.create_table(
            TableName=nm,
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
    r1 = cli(
        "dynamodb", "update-item", "--table-name", "Wf63A",
        "--key", '{"pk":{"S":"k"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"S":"in-a"}}',
    )
    assert r1.returncode == 0
    respB = ddb_client.get_item(TableName="Wf63B", Key={"pk": {"S": "k"}})
    assert "Item" not in respB
    itemA = from_item(ddb_client.get_item(TableName="Wf63A", Key={"pk": {"S": "k"}})["Item"])
    assert itemA["v"] == "in-a"
