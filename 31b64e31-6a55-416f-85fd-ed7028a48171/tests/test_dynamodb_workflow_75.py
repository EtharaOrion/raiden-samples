from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_numeric_pk_absent_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf76Tbl",
                 "--attribute-definitions", '[{"AttributeName":"id","AttributeType":"N"}]',
                 "--key-schema", '[{"AttributeName":"id","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf76Tbl",
                 "--item", '{"id":{"N":"5"},"v":{"S":"five"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Wf76Tbl",
                 "--key", '{"id":{"N":"999"}}')
    assert result.returncode == 0
    assert "Item" not in ddb_client.get_item(TableName="Wf76Tbl", Key={"id": {"N": "999"}})
    assert from_item(ddb_client.get_item(TableName="Wf76Tbl", Key={"id": {"N": "5"}})["Item"]) == {"id": 5, "v": "five"}
