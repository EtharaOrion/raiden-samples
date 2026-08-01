from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_overwrite_removes_old_attrs(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf60Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf60Tbl",
                 "--item", '{"pk":{"S":"r"},"old":{"S":"gone"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf60Tbl",
                 "--item", '{"pk":{"S":"r"},"fresh":{"S":"here"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf60Tbl", Key={"pk": {"S": "r"}})
    assert from_item(resp["Item"]) == {"pk": "r", "fresh": "here"}
