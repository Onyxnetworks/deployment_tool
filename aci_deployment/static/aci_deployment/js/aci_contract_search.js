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
                    var consumed_results = [
                        ['TEST1', 'TEST2', 'TEST3', 'TEST4'],
                        ['TEST1', 'TEST2', 'TEST3', 'TEST4'],
                        ['TEST1', 'TEST2', 'TEST3', 'TEST4'],
                        ['TEST2', 'TEST2', 'TEST3', 'TEST4'],
                        ['TEST2', 'TEST2', 'TEST5', 'TEST4'],
                        ['TEST2', 'TEST2', 'TEST5', 'TEST4'],
                    ];

                    console.log(consumed_results);
                    var table = $('#consumed_table').DataTable({

                        columnDefs: [

                        ],

                        columns: [
                            {
                                name: 'contract',
                                title: 'Contract Name',
                                class: 'text-center',
                            },
                            {
                                name: 'epg_name',
                                title: 'Provider EPG',
                                class: 'text-center',

                            },
                            {
                                title: 'Provider Networks',
                                class: 'text-center',

                            },
                            {
                                name: 'ports',
                                title: 'Ports',
                                class: 'text-center',

                            },
                        ],
                        data: data.result.consumed,
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