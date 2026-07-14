from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_absent_key_no_item(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf_Absent",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "Wf_Absent",
                 "--item", '{"pk":{"S":"here"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "get-item", "--table-name", "Wf_Absent",
                 "--key", '{"pk":{"S":"nothere"}}')
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName="Wf_Absent", Key={"pk": {"S": "nothere"}})
    assert "Item" not in resp
    assert "Item" in ddb_client.get_item(TableName="Wf_Absent", Key={"pk": {"S": "here"}})
