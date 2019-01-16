var frm = $('#f5_search');
var frm_all = $('#f5_search_all');
var rslt = $('#f5_results');


frm_all.submit(function () {
    document.getElementById("tablediv").style.visibility = "hidden";
    $.ajax({
        type: frm_all.attr('method'),
        url: frm_all.attr('action'),
        data: frm_all.serialize(),
        success: function (data) {
            if (data.task_id != null) {
                get_task_info(data.task_id);
            }},
        error: function (data) {
            document.getElementById("tablediv").style.visibility = "hidden";
            console.log("Something went wrong!");
        }
    });
    return false;


});

frm.submit(function () {
    document.getElementById("tablediv").style.visibility = "hidden";
    $.ajax({
        type: frm.attr('method'),
        url: frm.attr('action'),
        data: frm.serialize(),
        success: function (data) {
            if (data.task_id != null) {
                get_task_info(data.task_id);
            }},
        error: function (data) {
            document.getElementById("tablediv").style.visibility = "hidden";
            console.log("Something went wrong!");
        }
    });
    return false;


});

function build_result_table(data) {

    document.getElementById("loader").style.display = "none";
    document.getElementById("result_table").innerHTML = "";
    document.getElementById("tablediv").style.visibility = "visible";
    var results = data.result.data;
    for (i = 0, len = results.length, text = ""; i < len; i++) {
        f5_location = results[i].location;
        cert_name = results[i].cert_name;
        cert_expiration = results[i].cert_expiration;
        cert_status = results[i].cert_status;
        cert_status_message = results[i].cert_status_message;
        common_name = results[i].common_name;
        vs_list = results[i].vs_list;
        remaining_days = results[i].remaining_days;
        var tr = document.createElement("TR");
        var TABLE_TR = 'TABLE_TR_' + i;
        tr.setAttribute("id", TABLE_TR);
        tr.setAttribute("data-id", `${i}`);
        if (cert_status.includes('success')){
            tr.setAttribute("class", "success clickable-row");
        }
        if (cert_status.includes('danger')){
            tr.setAttribute("class", "danger clickable-row");
        }
        if (cert_status.includes('warning')){
            tr.setAttribute("class", "warning clickable-row");
        }
        document.getElementById("result_table").appendChild(tr);
        var search_results = [f5_location, cert_name, common_name, cert_expiration, remaining_days, cert_status_message];
        search_results.forEach(function(items) {
            var td = document.createElement("TD");
            td.setAttribute("style", "text-align: center; vertical-align: middle;");
            td.innerHTML = items;
            document.body.appendChild(td);
            document.getElementById(TABLE_TR).appendChild(td);
        });
    }


}


function build_detailed_table(results, result_index) {
    console.log('Building Detailed Data Table');
    document.getElementById("cert_data").scrollIntoView();
    document.getElementById("cert_body").innerHTML = "";
    document.getElementById("vs_body").innerHTML = "";

    cert_name = results[result_index].cert_name;
    cert_common_name = results[result_index].common_name;
    cert_expiration = results[result_index].cert_expiration;
    cert_remaining_days = results[result_index].remaining_days;
    cert_path = results[result_index].cert_fullPath;
    cert_issuer = results[result_index].cert_issuer;
    cert_key_size = results[result_index].cert_key_size;
    cert_sans = results[result_index].san;


    document.getElementById("cert_name").innerHTML = cert_name;
    document.getElementById("cert_common_name").innerHTML = cert_common_name;
    document.getElementById("cert_expiration").innerHTML = cert_expiration;
    document.getElementById("cert_remaining_days").innerHTML = cert_remaining_days;
    document.getElementById("cert_path").innerHTML = cert_path;
    document.getElementById("cert_issuer").innerHTML = cert_issuer;
    document.getElementById("cert_key_size").innerHTML = cert_key_size;
    document.getElementById("cert_sans").innerHTML = cert_sans;


    // Remove Hidden attribute from table
    document.getElementById("vs_data").style.visibility = "visible";

}


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
                rslt.html('Searching BigIP...');
            }
            else if (data.state == 'SUCCESS') {
                build_result_table(data)

                $(".clickable-row").click(function() {
                    console.log('click')
                    result_index = $(this).data('id');
                    console.log(result_index)
                    build_detailed_table(data.result, result_index)
                });

            }

            if (data.state != 'SUCCESS') {
                setTimeout(function () {
                    get_task_info(task_id)
                }, 1000);
            }},
        error: function (data) {
            document.getElementById("tablediv").style.visibility = "hidden";
            document.getElementById("loader").style.display = "none";
            rslt.html("Something went wrong!");success()
        }
    });
}
