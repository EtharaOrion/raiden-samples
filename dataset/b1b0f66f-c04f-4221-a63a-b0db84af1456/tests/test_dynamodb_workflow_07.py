from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_nonkey_attr_fails(cli, ddb_client):
    ddb_client.create_table(
        TableName="WFQueryBad",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WFQueryBad", Item={"pk": {"S": "z"}, "color": {"S": "red"}})
    result = cli(
        "dynamodb", "query",
        "--table-name", "WFQueryBad",
        "--key-condition-expression", "color = :v",
        "--expression-attribute-values", '{":v":{"S":"red"}}',
    )
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
