var frm = $('#contract_search');
var rslt = $('#contract_results');


frm.submit(function () {
    document.getElementById("contract_data").style.visibility = "hidden";
    $.ajax({
        type: frm.attr('method'),
        url: frm.attr('action'),
        data: frm.serialize(),
        success: function (data) {
            if (data.task_id != null) {
                get_task_info(data.task_id);
            }
        },
        error: function (data) {
            document.getElementById("contract_data").style.visibility = "hidden";
            console.log("Something went wrong!");
        }
    });
    return false;
});

function get_task_info(task_id) {
    $.ajax({
            type: 'get',
            url: '/get_task_info/',
            data: {'task_id': task_id},
            success: function (data) {
                rslt.html('');
                if (data.state == 'PENDING') {
                    var loader = `<img src='/static/index/svg/spinner.svg'/>`;
                    document.getElementById("loader").style.display = "block";
                    document.getElementById("loader").innerHTML = loader;
                    rslt.html('Searching Contracts...');
                }
                else if (data.state == 'SUCCESS') {
                    console.log('Success');
                    document.getElementById("loader").style.display = "none";
                    document.getElementById("contract_data").style.visibility = "visible";

                    // Build Consumed Contracts Results table.
                    var consumed_results = [["power_up", "app", "10.193.101.2/32", "[]"], ["power_up", "app", "2222::65:1/32", "[]"], ["power_up", "app", "10.193.102.4/32", "[]"], ["power_up", "app", "10.193.102.2/32", "[]"], ["web", "Web", "10.193.101.3/32", "[]"], ["web", "Web", "2222::66:3/32", "[]"], ["web", "Web", "10.193.102.1/32", "[]"], ["web", "Web", "2222::65:3/32", "[]"], ["web", "Web", "10.193.102.1/32", "[]"], ["web", "Web", "10.193.102.3/32", "[]"], ["web", "Web", "2222::66:3/32", "[]"], ["web", "Web", "2222::66:1/32", "[]"], ["web", "Web", "10.193.101.3/32", "[]"], ["web", "Web", "10.193.102.3/32", "[]"], ["web", "Web", "2222::66:1/32", "[]"], ["web", "Web", "2222::65:3/32", "[]"]];
                    console.log(consumed_results);
                    var table = $('#consumed_table').DataTable({

                        columns: [
                            {
                                name: 'contract',
                                title: 'Contract Name',
                            },
                            {
                                name: 'epg_name',
                                title: 'Provider EPG',
                            },
                            {
                                title: 'Provider Networks',
                            },
                            {
                                name: 'ports',
                                title: 'Ports',
                            },
                        ],
                        data: consumed_results,
                        rowsGroup: [
                            // Always the array (!) of the column-selectors in specified order to which rows groupping is applied
                            // (column-selector could be any of specified in https://datatables.net/reference/type/column-selector)
                            'contract:name',
                            'epg_name:name',
                            'ports:name',
                            0,
                            2
                        ],
                        pageLength: '20',
                    });
                }

                if (data.state != 'SUCCESS') {
                    setTimeout(function () {
                        get_task_info(task_id)
                    }, 1000);
                }
            },

            error: function (data) {
                document.getElementById("contract_data").style.visibility = "hidden";
                document.getElementById("loader").style.display = "none";
                rslt.html("Something went wrong!");
                success()
            }
        },
    );
}