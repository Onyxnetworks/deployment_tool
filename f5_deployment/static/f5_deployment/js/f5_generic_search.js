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
                <!-- Clear Old table Data -->
                document.getElementById("result_table").innerHTML = "";
                document.getElementById("tablediv").style.visibility = "visible";
                var results = data.result;
                for (i = 0, len = results.length, text = ""; i < len; i++) {
                    location = results[i].location;
                    vs_name = results[i].vs_name;
                    //AppProfile = results[i].AppProfile;
                    vs_status = results[i].vs_status;
                    pool_name = results[i].pool_name;
                    pool_status = results[i].pool_status;
                    if (vs_status.includes('available')) {
                        var vs_status_img = "<img src='{% static 'f5_deployment/img/status_circle_green.png' %}' class='img-responsive' alt='Responsive image'>"
                    }
                    if (vs_status.includes('offline')) {
                        var vs_status_img = "<img src='{% static 'f5_deployment/img/status_diamond_red.png' %}' class='img-responsive' alt='Responsive image'>"
                    }
                    if (vs_status.includes('unknown')) {
                        var vs_status_img = "<img src='{% static 'f5_deployment/img/status_square_blue.png' %}' class='img-responsive' alt='Responsive image'>"
                    }
                    if (pool_status.includes('available')) {
                        var pool_status_img = "<img src='{% static 'f5_deployment/img/status_circle_green.png' %}' class='img-responsive' alt='Responsive image'>"
                    }
                    if (pool_status.includes('offline')) {
                        var pool_status_img = "<img src='{% static 'f5_deployment/img/status_diamond_red.png' %}' class='img-responsive' alt='Responsive image'>"
                    }
                    if (pool_status.includes('unknown')) {
                        var pool_status_img = "<img src='{% static 'f5_deployment/img/status_square_blue.png' %}' class='img-responsive' alt='Responsive image'>"
                    }
                    var tr = document.createElement("TR");
                    var TABLE_TR = 'TABLE_TR' + i
                    tr.setAttribute("id", TABLE_TR);
                    document.getElementById("result_table").appendChild(tr);
                    var search_results = [location, vs_name, test, vs_status_img, pool_name, pool_status_img]
                    search_results.forEach(function(items) {
                        var td = document.createElement("TD");
                        td.setAttribute("style", "text-align: center; vertical-align: middle;");
                        td.innerHTML = items;
                        document.body.appendChild(td);
                        document.getElementById(TABLE_TR).appendChild(td);
                    });}

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