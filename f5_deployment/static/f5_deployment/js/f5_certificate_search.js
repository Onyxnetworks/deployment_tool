var frm = $('#f5_search');
var rslt = $('#f5_results');

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
        var search_results = [f5_location, cert_name, common_name, cert_expiration, cert_status_message];
        search_results.forEach(function(items) {
            var td = document.createElement("TD");
            td.setAttribute("style", "text-align: center; vertical-align: middle;");
            td.innerHTML = items;
            document.body.appendChild(td);
            document.getElementById(TABLE_TR).appendChild(td);
        });
    }


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
