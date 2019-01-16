var frm = $('#f5_search');
var frm_all = $('#f5_search_all');
var rslt = $('#f5_results');


frm_all.submit(function () {
    document.getElementById("tablediv").style.visibility = "hidden";
    document.getElementById("cert_data").style.visibility = "hidden";

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
            document.getElementById("cert_data").style.visibility = "hidden";
            console.log("Something went wrong!");
        }
    });
    return false;


});

frm.submit(function () {
    document.getElementById("tablediv").style.visibility = "hidden";
    document.getElementById("cert_data").style.visibility = "hidden";
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
            document.getElementById("cert_data").style.visibility = "hidden";
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

// Function to convert intigers to a readable format eg 1000 becomes 1k
function m(n,d){x=(''+n).length,p=Math.pow,d=p(10,d)
    x-=x%3
    return Math.round(n*d/p(10,x))/d+" kMGTPE"[x/3]}

function build_detailed_table(results, result_index) {
    document.getElementById("vs_body").innerHTML = '';
    console.log('Building Detailed Data Table');
    document.getElementById("cert_data").scrollIntoView();

    cert_name = results[result_index].cert_name;
    cert_common_name = results[result_index].common_name;
    cert_expiration = results[result_index].cert_expiration;
    cert_remaining_days = results[result_index].remaining_days;
    cert_path = results[result_index].cert_fullPath;
    cert_issuer = results[result_index].cert_issuer;
    cert_sans = results[result_index].san;

    document.getElementById("cert_name").innerHTML = cert_name;
    document.getElementById("cert_common_name").innerHTML = cert_common_name;
    document.getElementById("cert_expiration").innerHTML = cert_expiration;
    document.getElementById("cert_remaining_days").innerHTML = cert_remaining_days;
    document.getElementById("cert_path").innerHTML = cert_path;
    document.getElementById("cert_issuer").innerHTML = cert_issuer;

    cert_sans.forEach(function(items) {

        sre = `items<br>`
        document.getElementById("cert_sans").insertAdjacentHTML( 'beforeend', str );
        });



    vs_list = results[result_index].vs_list;
    for (i = 0, len = vs_list.length, text = ""; i < len; i++) {
        vs_name = vs_list[i].vs_name;
        vs_state = vs_list[i].vs_state;
        vs_port = vs_list[i].vs_port;
        vs_destination = vs_list[i].vs_destination;
        vs_admin_state = vs_list[i].vs_admin_state;
        vs_state_reason = vs_list[i].vs_state_reason;
        vs_bits_in = m(vs_list[i].vs_bits_in, 2);
        vs_bits_out = m(vs_list[i].vs_bits_out, 2);
        vs_packets_in = m(vs_list[i].vs_packets_in, 2);
        vs_packets_out = m(vs_list[i].vs_packets_out, 2);
        vs_conn_current = m(vs_list[i].vs_conn_current, 2);
        vs_conn_max = m(vs_list[i].vs_conn_max, 2);
        vs_conn_total = m(vs_list[i].vs_conn_total, 2);

        if (vs_admin_state.includes('disabled')){
            if (vs_state.includes('available')) {
                vs_status_img = `<img src='/static/f5_deployment/img/status_circle_black.png' class='img-responsive center-block' alt='vs_available' title=${vs_state_reason}">`
            }
            if (vs_state.includes('offline')) {
                vs_status_img = `<img src='/static/f5_deployment/img/status_diamond_black.png' class='img-responsive center-block' alt='vs_offline' title="${vs_state_reason}">`
            }
            if (vs_state.includes('unknown')) {
                vs_status_img = `<img src='/static/f5_deployment/img/status_square_black.png' class='img-responsive center-block' alt='vs_unknown' title="${vs_state_reason}">`
            }
        }
        if (vs_admin_state.includes('enabled')){
            if (vs_state.includes('available')) {
                vs_status_img = `<img src='/static/f5_deployment/img/status_circle_green.png' class='img-responsive center-block' alt='vs_available' title="${vs_state_reason}">`
            }
            if (vs_state.includes('offline')) {
                vs_status_img = `<img src='/static/f5_deployment/img/status_diamond_red.png' class='img-responsive center-block' alt='vs_offline' title="${vs_state_reason}">`
            }
            if (vs_state.includes('unknown')) {
                vs_status_img = `<img src='/static/f5_deployment/img/status_square_blue.png' class='img-responsive center-block' alt='vs_unknown' title="${vs_state_reason}">`
            }
        }

        var vs_tr = document.createElement("TR");
        var vs_table_tr = 'vs_table_tr' + i;
        vs_tr.setAttribute("id", vs_table_tr);
        document.getElementById("vs_body").appendChild(vs_tr);
        var vs_details = [vs_status_img, vs_name, vs_destination, vs_port, vs_bits_in, vs_bits_out, vs_packets_in, vs_packets_out, vs_conn_current, vs_conn_max, vs_conn_total];
        vs_details.forEach(function(items) {
            var vs_table_td = document.createElement("TD");
            vs_table_td.setAttribute("style", "text-align: center; vertical-align: middle;");
            vs_table_td.innerHTML = items;
            document.body.appendChild(vs_table_td);
            document.getElementById(vs_table_tr).appendChild(vs_table_td);
        });
    }    
    
    
    // Remove Hidden attribute from table
    document.getElementById("cert_data").style.visibility = "visible";

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
                    result_index = $(this).data('id');
                    build_detailed_table(data.result.data, result_index)
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
