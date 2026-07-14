from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_expression_errors(cli, ddb_client):
    table_name = "QueryErrTbl"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table_name,
        Item={"pk": {"S": "a"}},
    )
    # Query against a table that does not exist -> ResourceNotFoundException
    result = cli(
        "dynamodb", "query",
        "--table-name", "NoSuchQueryTable",
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", '{":v":{"S":"a"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr