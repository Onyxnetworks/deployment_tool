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
                    var consumed_results = data.result.consumed;
                    table_ref = '#consumed_table';
                    // Type is the text to put in the Provider/Consumer column.
                    type = 'Provider';
                    build_data_table(table_ref, type, consumed_results);

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


function build_data_table(table_ref, type, data) {
    var table = $(table_ref).DataTable({

        retrieve: true,
        responsive: true,
        "lengthMenu": [[-1, 25, 50, 100], ["All", 25, 50, 100]],
        columnDefs: [
            { targets: '_all', class: 'text-center' }
            ],

        columns: [
            {
                name: 'contract',
                title: 'Contract Name',
                style: 'vertical-align: middle'
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
                title: 'Filters',
            },
        ],
        data: data,
        rowsGroup: [
            // Always the array (!) of the column-selectors in specified order to which rows groupping is applied
            // (column-selector could be any of specified in https://datatables.net/reference/type/column-selector)
            'contract:name',
            'epg_name:name',
            'ports:name',
            0,
            2
        ],
    });
}