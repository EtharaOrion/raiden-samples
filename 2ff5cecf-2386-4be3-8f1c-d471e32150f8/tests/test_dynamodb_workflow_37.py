from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_no_condition_defaults(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf38Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf38Tbl",
        "--key", '{"pk":{"S":"z"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"S":"created"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf38Tbl", Key={"pk": {"S": "z"}})["Item"])
    assert item["v"] == "created"
