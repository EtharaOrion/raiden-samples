from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_nonkey_attr_fails(ddb_client, cli, tmp_path):
    ddb_client.create_table(
        TableName="WfQBad1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WfQBad1", Item={"pk": {"S": "p"}, "other": {"S": "z"}})
    result = cli(
        "dynamodb", "query",
        "--table-name", "WfQBad1",
        "--key-condition-expression", "other = :v",
        "--expression-attribute-values", '{":v":{"S":"z"}}',
    )
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
