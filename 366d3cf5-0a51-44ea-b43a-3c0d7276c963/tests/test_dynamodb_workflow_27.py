from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_bool_null(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf28",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf28",
                 "--item", '{"pk":{"S":"b"},"flag":{"BOOL":true},"nn":{"NULL":true}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf28", Key={"pk": {"S": "b"}})
    assert from_item(resp["Item"]) == {"pk": "b", "flag": True, "nn": None}
