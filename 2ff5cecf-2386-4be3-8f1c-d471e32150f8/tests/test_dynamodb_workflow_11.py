from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_then_update_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf12Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "delete-table", "--table-name", "Wf12Tbl")
    assert result.returncode == 0
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf12Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"x"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
