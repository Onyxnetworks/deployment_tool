var frm = $('#f5_search');
var rslt = $('#f5_results');


function JSconfirm(action, request_type, f5_selected_items, f5_selected_items_name)
{
	swal({
    title: "Are you sure you want to " + action + " these items?",
    text: f5_selected_items_name,
    type: "warning",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Yes",
    cancelButtonText: "No",
    closeOnConfirm: false,
    closeOnCancel: false },
    function(isConfirm){
        if (isConfirm)
    {
        set_status_deploy(action, request_type, f5_selected_items);
        swal('Changes being deployed.');
        }
        else {
            f5_selected_items.length = 0;
            swal("No changes will be made!");
            } });
}


function refresh_search_info() {
    post_data = {'f5_search': search_string, 'request_type': request_type};
    console.log('Updating Results');
    $.ajax({
        type: "POST",
        url: '/f5/generic_search/',
        //traditional: true,
        //processData: false,
        //dataType: 'json',
        //contentType: 'application/json',
        data: post_data,
        success: function (data) {
            if (data.task_id != null) {
                console.log('Search Task ID: ' + data.task_id);
                get_refresh_task_info(data.task_id, f5_selected_items_index)
            }},
        error: function (data) {
            console.log("Something went wrong!");
        }
    });

}

function get_refresh_task_info(task_id, f5_selected_items_index) {
    $.ajax({
        type: 'get',
        url: '/get_task_info/',
        data: {'task_id': task_id},
        success: function (data) {
            rslt.html('');
            if (data.state == 'PENDING') {
                var loader = `<img src='/static/index/svg/spinner.svg'/>`;
                //document.getElementById("loader").style.display = "block";
                //document.getElementById("loader").innerHTML = loader;
                rslt.html('Updating Result Data...');
            }
            else if (data.state == 'SUCCESS') {
                build_result_table(data);
                var results = data.result.data;
                build_detailed_table(results, f5_selected_items_index);

                $(".clickable-row").click(function() {
                    $('.checkbox:checked').each(function() {
                        $(this).prop('checked', false);
                    });
                    result_index = $(this).data('id');
                    window.f5_selected_items_index = ($(this).data('id'));
                    build_detailed_table(results, result_index)
                });

            }
            if (data.state != 'SUCCESS') {
                setTimeout(function () {
                    get_refresh_task_info(task_id, f5_selected_items_index)
                }, 1000);
            }},
        error: function (data) {
            rslt.html("Something went wrong!");success()
        }
    });}

function build_detailed_table(results, result_index) {
    //document.getElementById("vs_detail_row").removeAttribute("data-url");
    console.log('Building Detailed Data Table');
    document.getElementById("vs_data").scrollIntoView();
    document.getElementById("nodes_body").innerHTML = "";
    document.getElementById("vs_body").innerHTML = "";
    //var result_index = $(this).data('url');
    var vs_self_link = results[result_index].vs_selfLink;
    var vs_partition = results[result_index].vs_partition;
    var f5_location = results[result_index].location;
    var vs_name = results[result_index].vs_name;
    var vs_ip = results[result_index].vs_ip;
    var vs_port = results[result_index].vs_port;
    var vs_status = results[result_index].vs_state;
    var vs_admin_state = results[result_index].vs_admin_state;
    var vs_state_reason = results[result_index].vs_state_reason;
    var pool_name = results[result_index].vs_pool.pool_name;
    var pool_admin_state = results[result_index].vs_pool.pool_admin_state;
    var pool_status = results[result_index].vs_pool.pool_state;
    var pool_state_reason = results[result_index].vs_pool.pool_state_reason;
    var vs_bits_in = m(results[result_index].vs_stats.vs_bits_in, 2);
    var vs_bits_out = m(results[result_index].vs_stats.vs_bits_out, 2);
    var vs_packets_in = m(results[result_index].vs_stats.vs_packets_in, 2);
    var vs_packets_out = m(results[result_index].vs_stats.vs_packets_out, 2);
    var vs_conn_current = m(results[result_index].vs_stats.vs_conn_current, 2);
    var vs_conn_max = m(results[result_index].vs_stats.vs_conn_max, 2);
    var vs_conn_total = m(results[result_index].vs_stats.vs_conn_total, 2);
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
        var pool_bits_in = m(results[result_index].vs_pool.pool_stats.pool_bits_in, 2);
        var pool_bits_out = m(results[result_index].vs_pool.pool_stats.pool_bits_out, 2);
        var pool_packets_in = m(results[result_index].vs_pool.pool_stats.pool_packets_in, 2);
        var pool_packets_out = m(results[result_index].vs_pool.pool_stats.pool_packets_out, 2);
        var pool_conn_current = m(results[result_index].vs_pool.pool_stats.pool_conn_current, 2);
        var pool_conn_max = m(results[result_index].vs_pool.pool_stats.pool_conn_max, 2);
        var pool_conn_total = m(results[result_index].vs_pool.pool_stats.pool_conn_total, 2);
        var pool_requests_total = m(results[result_index].vs_pool.pool_stats.pool_requests_total, 2);
        var pool_requests_depth = m(results[result_index].vs_pool.pool_stats.pool_requests_depth, 2);
        var pool_requests_max_age = m(results[result_index].vs_pool.pool_stats.pool_requests_max_age, 2);
        var pool_active_members = results[result_index].vs_pool.pool_active_members;
        var pool_available_members = results[result_index].vs_pool.pool_available_members;

        if (pool_admin_state.includes('enabled')){
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

        if (pool_admin_state.includes('disabled')){
            if (pool_status.includes('available')) {
                var pool_status_img = `<img src='/static/f5_deployment/img/status_circle_black.png' class='img-responsive center-block' alt='pool_available' title="${pool_state_reason}">`
            }
            if (pool_status.includes('offline')) {
                var pool_status_img = `<img src='/static/f5_deployment/img/status_diamond_black.png' class='img-responsive center-block' alt='pool_offline' title="${pool_state_reason}">`
            }
            if (pool_status.includes('unknown')) {
                var pool_status_img = `<img src='/static/f5_deployment/img/status_square_black.png' class='img-responsive center-block' alt='pool_unknown' title="${pool_state_reason}">`
            }
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
            var node_self_link = node_results[ni].node_selfLink;
            var node_admin_state = node_results[ni].node_admin_state;
            var node_name = node_results[ni].node_name;
            var node_port = node_results[ni].node_port;
            var node_state = node_results[ni].node_state;
            var node_state_reason = node_results[ni].node_state_reason;
            var node_address = node_results[ni].node_address;
            var node_bits_in = m(node_results[ni].node_stats.node_bits_in, 2);
            var node_bits_out = m(node_results[ni].node_stats.node_bits_out, 2);
            var node_packets_in = m(node_results[ni].node_stats.node_packets_in, 2);
            var node_packets_out = m(node_results[ni].node_stats.node_packets_out, 2);
            var node_conn_current = m(node_results[ni].node_stats.node_conn_current, 2);
            var node_conn_max = m(node_results[ni].node_stats.node_conn_max, 2);
            var node_conn_total = m(node_results[ni].node_stats.node_conn_total, 2);
            var node_requests_total = m(node_results[ni].node_stats.node_requests_total, 2);
            var node_requests_depth = m(node_results[ni].node_stats.node_requests_depth, 2);
            var node_requests_max_age = m(node_results[ni].node_stats.node_requests_max_age, 2);
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
            node_tr.setAttribute("data-url", `${node_self_link}`);
            node_tr.setAttribute("data-id", `${result_index}`);
            node_tr.setAttribute("data-name", `${node_name}`);
            var node_table_tr = 'node_table_tr' + ni;
            var checkbox_id = 'node_checkbox_' + ni;
            var node_checkbox = `<input type="checkbox" class="checkbox" id="checkbox">`;
            node_tr.setAttribute("id", node_table_tr);
            document.getElementById("nodes_body").appendChild(node_tr);
            var node_details = [node_checkbox, node_status_img, node_name, node_address, node_bits_in, node_bits_out, node_packets_in, node_packets_out, node_conn_current, node_conn_max, node_conn_total, node_requests_total, node_requests_depth, node_requests_max_age]
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
    var vs_tr = document.createElement("TR");
    vs_tr.setAttribute("data-partition", `${vs_partition}`);
    vs_tr.setAttribute("data-url", `${vs_self_link}`);
    vs_tr.setAttribute("data-id", `${result_index}`);
    vs_tr.setAttribute("data-name", `${vs_name}`);
    var vs_table_tr = 'vs_table_tr';
    var vs_checkbox = `<input type="checkbox" class="checkbox" id="checkbox">`;
    vs_tr.setAttribute("id", vs_table_tr);
    document.getElementById("vs_body").appendChild(vs_tr);
    var vs_details = [vs_checkbox, vs_status_img, vs_name, vs_ip, vs_port, vs_bits_in, vs_bits_out, vs_packets_in, vs_packets_out, vs_conn_current, vs_conn_max, vs_conn_total]
    vs_details.forEach(function(items) {
        var vs_table_td = document.createElement("TD");
        vs_table_td.setAttribute("style", "text-align: center; vertical-align: middle;");
        vs_table_td.innerHTML = items;
        document.body.appendChild(vs_table_td);
        document.getElementById(vs_table_tr).appendChild(vs_table_td);
    });

    // Remove Hidden attribute from table
    document.getElementById("vs_data").style.visibility = "visible";




}

function build_result_table(data) {

    document.getElementById("loader").style.display = "none";
    document.getElementById("result_table").innerHTML = "";
    document.getElementById("tablediv").style.visibility = "visible";
    //document.getElementById("vs_data_body").innerHTML = "";
    var results = data.result.data;
    window.search_string = data.result.search.search_string;
    window.request_type = data.result.search.request_type;
    for (i = 0, len = results.length, text = ""; i < len; i++) {
        f5_location = results[i].location;
        vs_name = results[i].vs_name;
        vs_ip = results[i].vs_ip;
        vs_status = results[i].vs_state;
        vs_admin_state = results[i].vs_admin_state;
        vs_state_reason = results[i].vs_state_reason;
        pool_name = results[i].vs_pool.pool_name;
        pool_status = results[i].vs_pool.pool_state;
        pool_admin_state = results[i].vs_pool.pool_admin_state;
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
            if (pool_admin_state.includes('enabled')){
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
            if (pool_admin_state.includes('disabled')){
                if (pool_status.includes('available')) {
                    var pool_status_img = `<img src='/static/f5_deployment/img/status_circle_black.png' class='img-responsive center-block' alt='pool_available' title="${pool_state_reason}">`
                }
                if (pool_status.includes('offline')) {
                    var pool_status_img = `<img src='/static/f5_deployment/img/status_diamond_black.png' class='img-responsive center-block' alt='pool_offline' title="${pool_state_reason}">`
                }
                if (pool_status.includes('unknown')) {
                    var pool_status_img = `<img src='/static/f5_deployment/img/status_square_black.png' class='img-responsive center-block' alt='pool_unknown' title="${pool_state_reason}">`
                }
            }
        }
        if (pool_name == 'none'){
            var pool_status_img = ''
        }
        var tr = document.createElement("TR");
        var TABLE_TR = 'TABLE_TR_' + i
        tr.setAttribute("id", TABLE_TR);
        tr.setAttribute("data-id", `${i}`);
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


}

function set_status(action, request_type) {
    // Create empty list
    console.log('Action Button pressed.');
    var f5_selected_items = [];
    var f5_selected_items_name = [];
    if (request_type == 'node'){
        var checkedItems = $('#nodes_table input[type="checkbox"]:checked').each(function() {

            // Add selected items to the selected_items list.
            f5_selected_items.push($(this).parents('tr').data('url'));
            f5_selected_items_name.push($(this).parents('tr').data('name'));
        });
    }
    if (request_type == 'vs'){
        checkedItems = $('#vs_table input[type="checkbox"]:checked').each(function() {

            // Add selected items to the selected_items list.
            f5_selected_items.push($(this).parents('tr').data('url'));
            f5_selected_items_name.push($(this).parents('tr').data('name'));

        });
    }

    console.log(f5_selected_items);
    if (!checkedItems.length) {
        console.log('Nothing Checked')
    // Nothing was checked
    }
    else {
        JSconfirm(action, request_type, f5_selected_items, f5_selected_items_name);
    }
}

function set_status_deploy(action, request_type, f5_selected_items){
    // Post call to go and disable items.
    post_data = JSON.stringify({'action': action, 'request_type': request_type, 'f5_selected_items': f5_selected_items});
    $.ajax({
        type: "POST",
        url: '/f5/f5_disable_enable_push/',
        dataType: 'json',
        contentType: 'application/json',
        //traditional: true,
        data: post_data,
        success: function (data) {
            if (data.task_id != null) {
                console.log('Function Task ID: ' + data.task_id);
                // Now post call to refresh data.
                refresh_search_info()
            }},
        error: function (data) {
            //document.getElementById("tablediv").style.visibility = "hidden";
            //document.getElementById("vs_data").style.visibility = "hidden";
            console.log("Something went wrong!");
        }
    });

}

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

// Function to convert intigers to a readable format eg 1000 becomes 1k
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
                var loader = `<img src='/static/index/svg/spinner.svg'/>`;
                document.getElementById("loader").style.display = "block";
                document.getElementById("loader").innerHTML = loader;
                rslt.html('Searching BigIP...');
            }
            else if (data.state == 'SUCCESS') {

                build_result_table(data);

                //var result_table = $('#result_table_header').DataTable({
                //    retrieve: true,
                //    responsive: true,
                //    destroy: true,
                //    "language": {
                //        "search": "Filter records:"
                //    },
                //});

                //$('#result_table_header').on( 'click', 'tr', function () {
                    //var result_index = result_table.row( this ).id().split("_")[2];
                    //alert( 'Clicked row id '+result_index );
                //} );

                var results = data.result.data;
                $(".clickable-row").click(function() {
                    $('.checkbox:checked').each(function() {
                        $(this).prop('checked', false);
                    });


                    result_index = $(this).data('id');
                    window.f5_selected_items_index = ($(this).data('id'));
                    build_detailed_table(results, result_index)
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


