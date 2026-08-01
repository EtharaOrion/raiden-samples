from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_reserved_then_delete_table(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf79Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    r1 = cli(
        "dynamodb", "update-item", "--table-name", "Wf79Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET Name = :v",
        "--expression-attribute-values", '{":v":{"S":"x"}}',
    )
    assert r1.returncode != 0
    assert "ValidationException" in r1.stderr
    rd = cli("dynamodb", "delete-table", "--table-name", "Wf79Tbl")
    assert rd.returncode == 0
    assert "Wf79Tbl" not in ddb_client.list_tables()["TableNames"]
