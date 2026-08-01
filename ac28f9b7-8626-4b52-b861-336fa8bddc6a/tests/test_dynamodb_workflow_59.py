from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_list_membership_two_from_three(cli, ddb_client):
    for name in ["Wf60X", "Wf60Y"]:
        ddb_client.create_table(
            TableName=name,
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
    result = cli("dynamodb", "put-item", "--table-name", "Wf60X",
                 "--item", '{"pk":{"S":"a"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf60Y",
                 "--item", '{"pk":{"S":"b"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    names = set(ddb_client.list_tables()["TableNames"])
    assert {"Wf60X", "Wf60Y"}.issubset(names)
