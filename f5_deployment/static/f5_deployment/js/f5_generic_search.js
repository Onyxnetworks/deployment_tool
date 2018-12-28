var frm = $('#f5_search');
var rslt = $('#f5_results');

frm.submit(function () {
    document.getElementById("tablediv").style.visibility = "hidden";
    document.getElementById("vs_data").style.visibility = "hidden";
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
            document.getElementById("vs_data").style.visibility = "hidden";
            console.log("Something went wrong!");
        }
    });
    return false;


});

function m(n,d){x=(''+n).length,p=Math.pow,d=p(10,d)
    x-=x%3
    return Math.round(n*d/p(10,x))/d+" kMGTPE"[x/3]}

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
//                <!-- Clear Old table Data -->
                document.getElementById("result_table").innerHTML = "";
                document.getElementById("tablediv").style.visibility = "visible";
                //document.getElementById("vs_data_body").innerHTML = "";
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
                    pool_state_reason = results[i].vs_pool.pool_state_reason;
                    if (vs_admin_state.includes('disabled')){
                        if (vs_status.includes('available')) {
                            var vs_status_img = `<img src='/static/f5_deployment/img/status_circle_black.png' class='img-responsive center-block' alt='vs_available' title=${vs_state_reason}">`
                        }
                        if (vs_status.includes('offline')) {
                            var vs_status_img = `<img src='/static/f5_deployment/img/status_diamond_black.png' class='img-responsive center-block' alt='vs_offline' title="${vs_state_reason}">`
                        }
                        if (vs_status.includes('unknown')) {
                            var vs_status_img = `<img src='/static/f5_deployment/img/status_square_black.png' class='img-responsive center-block' alt='vs_unknown' title="${vs_state_reason}">`
                        }
                    }
                    if (vs_admin_state.includes('enabled')){
                        if (vs_status.includes('available')) {
                            var vs_status_img = `<img src='/static/f5_deployment/img/status_circle_green.png' class='img-responsive center-block' alt='vs_available' title="${vs_state_reason}">`
                        }
                        if (vs_status.includes('offline')) {
                            var vs_status_img = `<img src='/static/f5_deployment/img/status_diamond_red.png' class='img-responsive center-block' alt='vs_offline' title="${vs_state_reason}">`
                        }
                        if (vs_status.includes('unknown')) {
                            var vs_status_img = `<img src='/static/f5_deployment/img/status_square_blue.png' class='img-responsive center-block' alt='vs_unknown' title="${vs_state_reason}">`
                        }
                    }

                    if (pool_name != 'none'){
                        if (pool_status.includes('available')) {
                            var pool_status_img = `<img src='/static/f5_deployment/img/status_circle_green.png' class='img-responsive center-block' alt='pool_available' title="${pool_state_reason}">`
                        }
                        if (pool_status.includes('offline')) {
                            var pool_status_img = `<img src='/static/f5_deployment/img/status_diamond_red.png' class='img-responsive center-block' alt='pool_offline' title="${pool_state_reason}">`
                        }
                        if (pool_status.includes('unknown')) {
                            var pool_status_img = `<img src='/static/f5_deployment/img/status_square_blue.png' class='img-responsive center-block' alt='pool_unknown' title="${pool_state_reason}">`
                        }
                    }
                    if (pool_name == 'none'){
                        var pool_status_img = ''
                    }

                    var tr = document.createElement("TR");
                    var TABLE_TR = 'TABLE_TR' + i
                    tr.setAttribute("id", TABLE_TR);
                    tr.setAttribute("data-url", `${i}`);
                    if (vs_admin_state.includes('disabled')){
                        tr.setAttribute("class", "muted clickable-row");
                    }
                    else {
                        if (vs_status.includes('available')){
                            tr.setAttribute("class", "success clickable-row");
                        }
                        if (vs_status.includes('offline')){
                            tr.setAttribute("class", "danger clickable-row");
                        }
                        if (vs_status.includes('unknown')){
                            tr.setAttribute("class", "info clickable-row");
                        }
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
            $(".clickable-row").click(function() {
                document.getElementById("nodes_body").innerHTML = "";
                var result_index = $(this).data('url');
                var f5_location = results[result_index].location;
                var vs_name = results[result_index].vs_name;
                var vs_ip = results[result_index].vs_ip;
                var vs_port = results[result_index].vs_port;
                var vs_status = results[result_index].vs_state;
                var vs_admin_state = results[result_index].vs_admin_state;
                var vs_state_reason = results[result_index].vs_state_reason;
                var pool_name = results[result_index].vs_pool.pool_name;
                var pool_status = results[result_index].vs_pool.pool_state;
                var pool_state_reason = results[result_index].vs_pool.pool_state_reason;
                var vs_bits_in = m(parseInt(results[result_index].vs_stats.vs_bits_in));
                var vs_bits_out = results[result_index].vs_stats.vs_bits_out;
                var vs_packets_in = results[result_index].vs_stats.vs_packets_in;
                var vs_packets_out = results[result_index].vs_stats.vs_packets_out;
                var vs_conn_current = results[result_index].vs_stats.vs_conn_current;
                var vs_conn_max = results[result_index].vs_stats.vs_conn_max;
                var vs_conn_total = results[result_index].vs_stats.vs_conn_total;
                if (vs_admin_state.includes('disabled')){
                    if (vs_status.includes('available')) {
                        var vs_status_img = `<img src='/static/f5_deployment/img/status_circle_black.png' class='img-responsive center-block' alt='vs_available' title=${vs_state_reason}">`
                    }
                    if (vs_status.includes('offline')) {
                        var vs_status_img = `<img src='/static/f5_deployment/img/status_diamond_black.png' class='img-responsive center-block' alt='vs_offline' title="${vs_state_reason}">`
                    }
                    if (vs_status.includes('unknown')) {
                        var vs_status_img = `<img src='/static/f5_deployment/img/status_square_black.png' class='img-responsive center-block' alt='vs_unknown' title="${vs_state_reason}">`
                    }
                }
                if (vs_admin_state.includes('enabled')){
                    if (vs_status.includes('available')) {
                        var vs_status_img = `<img src='/static/f5_deployment/img/status_circle_green.png' class='img-responsive center-block' alt='vs_available' title="${vs_state_reason}">`
                    }
                    if (vs_status.includes('offline')) {
                        var vs_status_img = `<img src='/static/f5_deployment/img/status_diamond_red.png' class='img-responsive center-block' alt='vs_offline' title="${vs_state_reason}">`
                    }
                    if (vs_status.includes('unknown')) {
                        var vs_status_img = `<img src='/static/f5_deployment/img/status_square_blue.png' class='img-responsive center-block' alt='vs_unknown' title="${vs_state_reason}">`
                    }
                }
                if (pool_name != 'none'){
                    var pool_bits_in = results[result_index].vs_pool.pool_stats.pool_bits_in;
                    var pool_bits_out = results[result_index].vs_pool.pool_stats.pool_bits_out;
                    var pool_packets_in = results[result_index].vs_pool.pool_stats.pool_packets_in;
                    var pool_packets_out = results[result_index].vs_pool.pool_stats.pool_packets_out;
                    var pool_conn_current = results[result_index].vs_pool.pool_stats.pool_conn_current;
                    var pool_conn_max = results[result_index].vs_pool.pool_stats.pool_conn_max;
                    var pool_conn_total = results[result_index].vs_pool.pool_stats.pool_conn_total;
                    var pool_requests_total = results[result_index].vs_pool.pool_stats.pool_requests_total;
                    var pool_requests_depth = results[result_index].vs_pool.pool_stats.pool_requests_depth;
                    var pool_requests_max_age = results[result_index].vs_pool.pool_stats.pool_requests_max_age;
                    var pool_active_members = results[result_index].vs_pool.pool_active_members;
                    var pool_available_members = results[result_index].vs_pool.pool_available_members;

                    if (pool_status.includes('available')) {
                        var pool_status_img = `<img src='/static/f5_deployment/img/status_circle_green.png' class='img-responsive center-block' alt='pool_available' title="${pool_state_reason}">`
                    }
                    if (pool_status.includes('offline')) {
                        var pool_status_img = `<img src='/static/f5_deployment/img/status_diamond_red.png' class='img-responsive center-block' alt='pool_offline' title="${pool_state_reason}">`
                    }
                    if (pool_status.includes('unknown')) {
                        var pool_status_img = `<img src='/static/f5_deployment/img/status_square_blue.png' class='img-responsive center-block' alt='pool_unknown' title="${pool_state_reason}">`
                    }

                    document.getElementById("pool_detail_status").innerHTML = pool_status_img;
                    document.getElementById("pool_detail_name").innerHTML = pool_name;
                    document.getElementById("pool_detail_members").innerHTML = pool_active_members + '/' + pool_available_members;
                    document.getElementById("pool_detail_bits_in").innerHTML = pool_bits_in;
                    document.getElementById("pool_detail_bits_out").innerHTML = pool_bits_out;
                    document.getElementById("pool_detail_packets_in").innerHTML = pool_packets_in;
                    document.getElementById("pool_detail_packets_out").innerHTML = pool_packets_out;
                    document.getElementById("pool_detail_connections_current").innerHTML = pool_conn_current;
                    document.getElementById("pool_detail_connections_maximum").innerHTML = pool_conn_max;
                    document.getElementById("pool_detail_connections_total").innerHTML = pool_conn_total;
                    document.getElementById("pool_detail_requests_total").innerHTML = pool_requests_total;
                    document.getElementById("pool_detail_requests_depth").innerHTML = pool_requests_depth;
                    document.getElementById("pool_detail_requests_max_age").innerHTML = pool_requests_max_age;

                    var node_results = results[result_index].vs_nodes;
                    for (ni = 0, len = node_results.length, text = ""; ni < len; ni++) {
                        var node_admin_state = node_results[ni].node_admin_state;
                        var node_name = node_results[ni].node_name;
                        var node_port = node_results[ni].node_port;
                        var node_state = node_results[ni].node_state;
                        var node_state_reason = node_results[ni].node_state_reason;
                        var node_address = node_results[ni].node_address;
                        var node_bits_in = node_results[ni].node_stats.node_bits_in;
                        var node_bits_out = node_results[ni].node_stats.node_bits_out;
                        var node_packets_in = node_results[ni].node_stats.node_packets_in;
                        var node_packets_out = node_results[ni].node_stats.node_packets_out;
                        var node_conn_current = node_results[ni].node_stats.node_conn_current;
                        var node_conn_max = node_results[ni].node_stats.node_conn_max;
                        var node_conn_total = node_results[ni].node_stats.node_conn_total;
                        var node_requests_total = node_results[ni].node_stats.node_requests_total;
                        var node_requests_depth = node_results[ni].node_stats.node_requests_depth;
                        var node_requests_max_age = node_results[ni].node_stats.node_requests_max_age;
                        if (node_admin_state.includes('disabled')){
                            if (node_state.includes('available')) {
                                var node_status_img = `<img src='/static/f5_deployment/img/status_circle_black.png' class='img-responsive center-block' alt='node_available' title="${node_state_reason}">`
                            }
                            if (node_state.includes('offline')) {
                                var node_status_img = `<img src='/static/f5_deployment/img/status_diamond_black.png' class='img-responsive center-block' alt='node_offline' title="${node_state_reason}">`
                            }

                            if (node_state.includes('unknown')) {
                                var node_status_img = `<img src='/static/f5_deployment/img/status_square_black.png' class='img-responsive center-block' alt='node_unknown' title="${node_state_reason}">`
                            }
                        }
                        if (node_admin_state.includes('enabled')){
                            if (node_state.includes('available')) {
                                var node_status_img = `<img src='/static/f5_deployment/img/status_circle_green.png' class='img-responsive center-block' alt='node_available' title="${node_state_reason}">`
                            }
                            if (node_state.includes('offline')) {
                                var node_status_img = `<img src='/static/f5_deployment/img/status_diamond_red.png' class='img-responsive center-block' alt='node_offline' title="${node_state_reason}">`
                            }
                            if (node_state.includes('unknown')) {
                                var node_status_img = `<img src='/static/f5_deployment/img/status_square_blue.png' class='img-responsive center-block' alt='node_unknown' title="${node_state_reason}">`
                            }
                        }

                        var node_tr = document.createElement("TR");
                        var node_table_tr = 'node_table_tr' + ni;
                        node_tr.setAttribute("id", node_table_tr);
                        document.getElementById("nodes_body").appendChild(node_tr);
                        var node_details = [node_status_img, node_name, node_address, node_bits_in, node_bits_out, node_packets_in, node_packets_out, node_conn_current, node_conn_max, node_conn_total, node_requests_total, node_requests_depth, node_requests_max_age]
                        node_details.forEach(function(items) {
                            var node_table_td = document.createElement("TD");
                            node_table_td.setAttribute("style", "text-align: center; vertical-align: middle;");
                            node_table_td.innerHTML = items;
                            document.body.appendChild(node_table_td);
                            document.getElementById(node_table_tr).appendChild(node_table_td);
                        });
                    }

                }
                if (pool_name == 'none'){
                    document.getElementById("pool_detail_status").innerHTML = '';
                    document.getElementById("pool_detail_name").innerHTML = '';
                    document.getElementById("pool_detail_members").innerHTML = '';
                    document.getElementById("pool_detail_bits_in").innerHTML = '';
                    document.getElementById("pool_detail_bits_out").innerHTML = '';
                    document.getElementById("pool_detail_packets_in").innerHTML = '';
                    document.getElementById("pool_detail_packets_out").innerHTML = '';
                    document.getElementById("pool_detail_connections_current").innerHTML = '';
                    document.getElementById("pool_detail_connections_maximum").innerHTML = '';
                    document.getElementById("pool_detail_connections_total").innerHTML = '';
                    document.getElementById("pool_detail_requests_total").innerHTML = '';
                    document.getElementById("pool_detail_requests_depth").innerHTML = '';
                    document.getElementById("pool_detail_requests_max_age").innerHTML = '';

                    var pool_status_img = '';
                }
                document.getElementById("vs_data").style.visibility = "visible";
                document.getElementById("vs_detail_status").innerHTML = vs_status_img;
                document.getElementById("vs_detail_name").innerHTML = vs_name;
                document.getElementById("vs_detail_destination").innerHTML = vs_ip;
                document.getElementById("vs_detail_port").innerHTML = vs_port;
                document.getElementById("vs_detail_bits_in").innerHTML = vs_bits_in;
                document.getElementById("vs_detail_bits_out").innerHTML = vs_bits_out;
                document.getElementById("vs_detail_packets_in").innerHTML = vs_packets_in;
                document.getElementById("vs_detail_packets_out").innerHTML = vs_packets_out;
                document.getElementById("vs_detail_connections_current").innerHTML = vs_conn_current;
                document.getElementById("vs_detail_connections_maximum").innerHTML = vs_conn_max;
                document.getElementById("vs_detail_connections_total").innerHTML = vs_conn_total;
                });
            }

            if (data.state != 'SUCCESS') {
                setTimeout(function () {
                    get_task_info(task_id)
                }, 1000);
            }},
        error: function (data) {
            document.getElementById("tablediv").style.visibility = "hidden";
            rslt.html("Something went wrong!");success()
        }
    });
}

