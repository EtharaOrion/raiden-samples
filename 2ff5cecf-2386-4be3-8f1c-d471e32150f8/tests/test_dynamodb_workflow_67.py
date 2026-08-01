from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_numeric_key_pk(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf68Tbl",
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "N"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf68Tbl",
        "--key", '{"id":{"N":"42"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"S":"x"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf68Tbl", Key={"id": {"N": "42"}})["Item"])
    assert item["v"] == "x"
