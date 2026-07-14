from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_non_key_validation(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf11Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf11Tbl",
                 "--item", '{"pk":{"S":"q1"},"colr":{"S":"red"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "query", "--table-name", "Wf11Tbl",
                 "--key-condition-expression", "colr = :v",
                 "--expression-attribute-values", '{":v":{"S":"red"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf11Tbl", Key={"pk": {"S": "q1"}})
    assert "Item" in resp
