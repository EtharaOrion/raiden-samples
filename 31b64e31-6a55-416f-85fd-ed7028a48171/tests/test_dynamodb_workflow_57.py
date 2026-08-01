from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_recreate_after_inuse_error_still_usable(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf58Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "create-table", "--table-name", "Wf58Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode != 0
    assert "ResourceInUseException" in result.stderr
    result = cli("dynamodb", "put-item", "--table-name", "Wf58Tbl",
                 "--item", '{"pk":{"S":"post"},"v":{"S":"ok"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf58Tbl", Key={"pk": {"S": "post"}})
    assert from_item(resp["Item"]) == {"pk": "post", "v": "ok"}
