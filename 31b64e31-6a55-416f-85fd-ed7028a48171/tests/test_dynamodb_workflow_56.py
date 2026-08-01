from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_put_many_attrs_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf57Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf57Tbl",
                 "--item", '{"pk":{"S":"m"},"s":{"S":"str"},"n":{"N":"7"},"bl":{"BOOL":false}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf57Tbl", Key={"pk": {"S": "m"}})
    assert from_item(resp["Item"]) == {"pk": "m", "s": "str", "n": 7, "bl": False}
