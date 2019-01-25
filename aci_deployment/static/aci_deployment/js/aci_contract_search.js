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
                    console.log(data.result);

                    // Build Consumed Contracts Results table.
                    var consumed_results = data.result.consumed;
                    for (i = 0, len = consumed_results.length, text = ""; i < len; i++) {

                        contract_name = consumed_results[i].contract_name;
                        provider_list = consumed_results[i].provider_list;
                        port_list = consumed_results[i].port_list;
                        console.log(contract_name, provider_list, port_list)
                        port_list.forEach(function(items) {
                            port_str = items + `<br>`
                            document.getElementById("cert_sans").insertAdjacentHTML( 'beforeend', port_str );
                        });

                        contract_port_tr = document.createElement("TR");
                        contract_port_table_tr = 'contract_port_table_tr' + i;
                        contract_port_tr.setAttribute("id", contract_port_table_tr);
                        document.getElementById("consumed_body").appendChild(contract_port_tr);
                        contract_details = [contract_name, port_list];

                        contract_details.forEach(function(items) {
                            contract_table_td = document.createElement("TD");
                            contract_table_td.setAttribute("style", "text-align: center; vertical-align: middle;");
                            contract_table_td.setAttribute("rowspan", provider_list.length);
                            contract_table_td.innerHTML = items;
                            document.body.appendChild(contract_table_td);
                            document.getElementById(contract_port_table_tr).appendChild(contract_table_td);
                        });
                    }
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