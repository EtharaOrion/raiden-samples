from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_reserved_aliased_success(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf33Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf33Table",
                 "--item", '{"pk":{"S":"ra1"},"Status":{"S":"start"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf33Table",
                 "--key", '{"pk":{"S":"ra1"}}',
                 "--update-expression", "SET #s = :v",
                 "--expression-attribute-names", '{"#s":"Status"}',
                 "--expression-attribute-values", '{":v":{"S":"done"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf33Table", Key={"pk": {"S": "ra1"}})
    assert from_item(resp["Item"])["Status"] == "done"
