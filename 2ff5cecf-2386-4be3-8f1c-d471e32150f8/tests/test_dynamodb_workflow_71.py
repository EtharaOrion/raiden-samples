from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_get_confirms_item_member(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf72Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    r1 = cli(
        "dynamodb", "update-item", "--table-name", "Wf72Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"state"}',
        "--expression-attribute-values", '{":v":{"S":"ready"}}',
    )
    assert r1.returncode == 0
    r2 = cli(
        "dynamodb", "get-item", "--table-name", "Wf72Tbl",
        "--key", '{"pk":{"S":"a"}}',
    )
    assert r2.returncode == 0
    resp = ddb_client.get_item(TableName="Wf72Tbl", Key={"pk": {"S": "a"}})
    assert "Item" in resp and from_item(resp["Item"])["state"] == "ready"
