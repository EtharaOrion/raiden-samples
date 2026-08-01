from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_empty_string_value(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf63",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf63",
                 "--item", '{"pk":{"S":"e"},"note":{"S":""}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf63", Key={"pk": {"S": "e"}})
    assert from_item(resp["Item"]) == {"pk": "e", "note": ""}
