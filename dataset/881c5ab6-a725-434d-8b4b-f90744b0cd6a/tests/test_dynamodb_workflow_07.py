from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_getitem_missing_table_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblH",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    result = cli("dynamodb", "get-item", "--table-name", "WfTblH_missing",
                 "--key", '{"pk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
