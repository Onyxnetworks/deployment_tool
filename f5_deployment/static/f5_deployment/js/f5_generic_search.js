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
function get_task_info(task_id) {
    $.ajax({
        type: 'get',
        url: '/get_task_info/',
        data: {'task_id': task_id},
        success: function (data) {
            rslt.html('');
            if (data.state == 'PENDING') {
                rslt.html('Searching BigIP...');
            }
            else if (data.state == 'SUCCESS') {
                console.log("success");
//                <!-- Clear Old table Data -->
                document.getElementById("result_table").innerHTML = "";
                document.getElementById("tablediv").style.visibility = "visible";
                var results = data.result;
                for (i = 0, len = results.length, text = ""; i < len; i++) {
                    f5_location = results[i].location;
                    vs_name = results[i].vs_name;
                    vs_ip = results[i].vs_ip;
                    vs_status = results[i].vs_state;
                    vs_admin_state = results[i].vs_admin_state;
                    vs_state_reason = results[i].vs_state_reason;
                    pool_name = results[i].vs_pool.pool_name;
                    pool_status = results[i].vs_pool.pool_state;
                    if (vs_admin_state.includes('disabled')){
                        if (vs_status.includes('available')) {
                            var vs_status_img = "<img src='/static/f5_deployment/img/status_circle_black.png' class='img-responsive center-block' alt='vs_available' title='{{ vs_state_reason }}'>"
                        }
                        if (vs_status.includes('offline')) {
                            var vs_status_img = "<img src='/static/f5_deployment/img/status_diamond_black.png' class='img-responsive center-block' alt='vs_offline' title='{{ vs_state_reason }}'>"
                        }
                        if (vs_status.includes('unknown')) {
                            var vs_status_img = "<img src='/static/f5_deployment/img/status_square_black.png' class='img-responsive center-block' alt='vs_unknown' title='{{ vs_state_reason }}'>"
                        }
                    }
                    if (vs_admin_state.includes('enabled')){
                        if (vs_status.includes('available')) {
                            var vs_status_img = "<img src='/static/f5_deployment/img/status_circle_green.png' class='img-responsive center-block' alt='vs_available' title='{{ vs_state_reason }}'>"
                        }
                        if (vs_status.includes('offline')) {
                            var vs_status_img = "<img src='/static/f5_deployment/img/status_diamond_red.png' class='img-responsive center-block' alt='vs_offline' title='{{ vs_state_reason }}'>"
                        }
                        if (vs_status.includes('unknown')) {
                            var vs_status_img = "<img src='/static/f5_deployment/img/status_square_blue.png' class='img-responsive center-block' alt='vs_unknown' title='{{ vs_state_reason }}'>"
                        }
                    }

                    if (pool_status.includes('available')) {
                        var pool_status_img = "<img src='/static/f5_deployment/img/status_circle_green.png' class='img-responsive center-block' alt='pool_available' title='{{ vs_state_reason }}'>"
                    }
                    if (pool_status.includes('offline')) {
                        var pool_status_img = "<img src='/static/f5_deployment/img/status_diamond_red.png' class='img-responsive center-block' alt='pool_offline' title='{{ vs_state_reason }}'>"
                    }
                    if (pool_status.includes('unknown')) {
                        var pool_status_img = "<img src='/static/f5_deployment/img/status_square_blue.png' class='img-responsive center-block' alt='pool_unknown' title='{{ vs_state_reason }}'>"
                    }
                    var tr = document.createElement("TR");
                    var TABLE_TR = 'TABLE_TR' + i
                    tr.setAttribute("id", TABLE_TR);
                    if (vs_status.includes('available')){
                        tr.setAttribute("class", "success");
                    }
                    if (vs_status.includes('offline')){
                        tr.setAttribute("class", "danger");
                    }
                    if (vs_status.includes('unknown')){
                        tr.setAttribute("class", "info");
                    }
                    document.getElementById("result_table").appendChild(tr);
                    var search_results = [f5_location, vs_name, vs_ip, vs_status_img, pool_name, pool_status_img]
                    search_results.forEach(function(items) {
                        var td = document.createElement("TD");
                        td.setAttribute("style", "text-align: center; vertical-align: middle;");
                        td.innerHTML = items;
                        document.body.appendChild(td);
                        document.getElementById(TABLE_TR).appendChild(td);
                    });
            }

            }

            if (data.state != 'SUCCESS') {
                setTimeout(function () {
                    console.log("not success run task");
                    get_task_info(task_id)
                }, 1000);
            }},
        error: function (data) {
            document.getElementById("tablediv").style.visibility = "hidden";
            rslt.html("Something went wrong!");success()
        }
    });
}