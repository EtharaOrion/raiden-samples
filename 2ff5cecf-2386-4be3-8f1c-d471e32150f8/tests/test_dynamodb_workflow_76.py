from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_after_update_removes_absence(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf77Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    resp0 = ddb_client.get_item(TableName="Wf77Tbl", Key={"pk": {"S": "a"}})
    assert "Item" not in resp0
    r = cli(
        "dynamodb", "update-item", "--table-name", "Wf77Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"S":"now"}}',
    )
    assert r.returncode == 0
    resp1 = ddb_client.get_item(TableName="Wf77Tbl", Key={"pk": {"S": "a"}})
    assert "Item" in resp1
