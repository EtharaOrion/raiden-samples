from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_missing_key_after_update_other(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf55Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    r1 = cli(
        "dynamodb", "update-item", "--table-name", "Wf55Tbl",
        "--key", '{"pk":{"S":"exists"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"S":"x"}}',
    )
    assert r1.returncode == 0
    r2 = cli(
        "dynamodb", "get-item", "--table-name", "Wf55Tbl",
        "--key", '{"pk":{"S":"other"}}',
    )
    assert r2.returncode == 0
    resp = ddb_client.get_item(TableName="Wf55Tbl", Key={"pk": {"S": "other"}})
    assert "Item" not in resp
