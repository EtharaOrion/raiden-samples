from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_number_type_readback(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf41Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf41Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET price = :p",
        "--expression-attribute-values", '{":p":{"N":"19.99"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf41Tbl", Key={"pk": {"S": "a"}})
    assert resp["Item"]["price"]["N"] == "19.99"
