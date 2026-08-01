from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_after_multiple_updates(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf65Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    for i in range(3):
        r = cli(
            "dynamodb", "update-item", "--table-name", "Wf65Tbl",
            "--key", '{"pk":{"S":"a"}}',
            "--update-expression", "SET n = :v",
            "--expression-attribute-values", '{":v":{"N":"' + str(i) + '"}}',
        )
        assert r.returncode == 0
    rd = cli("dynamodb", "delete-table", "--table-name", "Wf65Tbl")
    assert rd.returncode == 0
    assert "Wf65Tbl" not in ddb_client.list_tables()["TableNames"]
