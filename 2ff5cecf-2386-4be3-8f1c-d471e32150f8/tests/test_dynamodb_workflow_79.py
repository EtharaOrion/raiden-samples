from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_three_then_list_membership(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf80Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    for k in ("p", "q", "r"):
        r = cli(
            "dynamodb", "update-item", "--table-name", "Wf80Tbl",
            "--key", '{"pk":{"S":"' + k + '"}}',
            "--update-expression", "SET seen = :v",
            "--expression-attribute-values", '{":v":{"BOOL":true}}',
        )
        assert r.returncode == 0
    rl = cli("dynamodb", "list-tables")
    assert rl.returncode == 0
    assert "Wf80Tbl" in ddb_client.list_tables()["TableNames"]
    for k in ("p", "q", "r"):
        item = from_item(ddb_client.get_item(TableName="Wf80Tbl", Key={"pk": {"S": k}})["Item"])
        assert item["seen"] is True
