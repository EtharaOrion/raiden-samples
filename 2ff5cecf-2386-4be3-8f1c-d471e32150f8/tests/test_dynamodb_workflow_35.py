from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_reserved_status_aliased_ok(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf36Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf36Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET #st = :v",
        "--expression-attribute-names", '{"#st":"Status"}',
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf36Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["Status"] == "active"
