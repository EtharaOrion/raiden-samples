from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multi_table_list_membership(cli, ddb_client):
    for name in ["Wf31A", "Wf31B", "Wf31C"]:
        ddb_client.create_table(
            TableName=name,
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
    result = cli("dynamodb", "put-item", "--table-name", "Wf31B",
                 "--item", '{"pk":{"S":"x"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    names = set(ddb_client.list_tables()["TableNames"])
    assert {"Wf31A", "Wf31B", "Wf31C"}.issubset(names)
