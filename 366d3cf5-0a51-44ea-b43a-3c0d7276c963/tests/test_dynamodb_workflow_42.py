from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_stringset_put(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf43",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf43",
                 "--item", '{"pk":{"S":"ss"},"tags":{"SS":["a","b","c"]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf43", Key={"pk": {"S": "ss"}})
    assert set(resp["Item"]["tags"]["SS"]) == {"a", "b", "c"}
