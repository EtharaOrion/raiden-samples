from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_then_success_second(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf56Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf56Tbl", Item={"pk": {"S": "a"}, "n": {"N": "1"}})
    r1 = cli(
        "dynamodb", "update-item", "--table-name", "Wf56Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET n = :new",
        "--condition-expression", "n = :bad",
        "--expression-attribute-values", '{":new":{"N":"2"},":bad":{"N":"9"}}',
    )
    assert r1.returncode != 0
    assert "ConditionalCheckFailedException" in r1.stderr
    r2 = cli(
        "dynamodb", "update-item", "--table-name", "Wf56Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET n = :new",
        "--condition-expression", "n = :ok",
        "--expression-attribute-values", '{":new":{"N":"2"},":ok":{"N":"1"}}',
    )
    assert r2.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf56Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["n"] == 2
