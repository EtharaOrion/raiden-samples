from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_delete_table_gone(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf50Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    r1 = cli(
        "dynamodb", "update-item", "--table-name", "Wf50Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"S":"x"}}',
    )
    assert r1.returncode == 0
    rd = cli("dynamodb", "delete-table", "--table-name", "Wf50Tbl")
    assert rd.returncode == 0
    r2 = cli(
        "dynamodb", "update-item", "--table-name", "Wf50Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"S":"y"}}',
    )
    assert r2.returncode != 0
    assert "ResourceNotFoundException" in r2.stderr
