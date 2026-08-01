from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_increment_chain(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf75Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf75Tbl", Item={"pk": {"S": "a"}, "c": {"N": "0"}})
    for _ in range(3):
        r = cli(
            "dynamodb", "update-item", "--table-name", "Wf75Tbl",
            "--key", '{"pk":{"S":"a"}}',
            "--update-expression", "ADD c :one",
            "--expression-attribute-values", '{":one":{"N":"1"}}',
        )
        assert r.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf75Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["c"] == 3
