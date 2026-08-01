from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_condition_on_missing_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "put-item", "--table-name", "Wf28NoTbl",
                 "--item", '{"pk":{"S":"x"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
