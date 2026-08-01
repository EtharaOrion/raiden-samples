from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_stringset_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf24Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf24Tbl",
                 "--item", '{"pk":{"S":"ss1"},"tags":{"SS":["a","b","c"]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf24Tbl", Key={"pk": {"S": "ss1"}})
    assert set(resp["Item"]["tags"]["SS"]) == {"a", "b", "c"}
