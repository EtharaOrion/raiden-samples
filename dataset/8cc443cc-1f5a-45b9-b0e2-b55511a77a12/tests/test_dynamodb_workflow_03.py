from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_item_missing_table(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfExistsTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    )
    assert "WfExistsTbl" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "get-item", "--table-name", "WfNoSuchTbl",
                 "--key", '{"pk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
