from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_list_tables_membership(cli, ddb_client, tmp_path):
    import json
    ddb_client.create_table(
        TableName="WfTblList1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfTblList1",
                 "--item", '{"pk":{"S":"l1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    names = set(json.loads(result.stdout)["TableNames"])
    assert "WfTblList1" in names
    assert "WfTblList1" in set(ddb_client.list_tables()["TableNames"])
