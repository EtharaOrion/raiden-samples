from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_remove_then_get(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf43Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    r1 = cli(
        "dynamodb", "update-item", "--table-name", "Wf43Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET tmp = :v",
        "--expression-attribute-values", '{":v":{"S":"here"}}',
    )
    assert r1.returncode == 0
    r2 = cli(
        "dynamodb", "update-item", "--table-name", "Wf43Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "REMOVE tmp",
    )
    assert r2.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf43Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert "tmp" not in item
