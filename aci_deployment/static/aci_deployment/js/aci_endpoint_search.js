var frm = $('#endpoint_search');
var rslt = $('#endpoint_results');


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
                var loader = `<img src='/static/index/svg/spinner.svg'/>`;
                document.getElementById("loader").style.display = "block";
                document.getElementById("loader").innerHTML = loader;
                rslt.html('Searching Endpoints...');
            }
            else if (data.state == 'SUCCESS') {
                <!-- Clear Old table Data -->
                if ($.fn.DataTable.isDataTable("#endpoint_table")){
                    $('#endpoint_table').DataTable().clear().destroy();
                }
                document.getElementById("loader").style.display = "none";
                document.getElementById("result_table").innerHTML = "";
                document.getElementById("tablediv").style.visibility = "visible";
                var results = data.result;
                for (i = 0, len = results.length, text = ""; i < len; i++) {
                    Location = results[i].Location;
                    Tenant = results[i].Tenant;
                    AppProfile = results[i].AppProfile;
                    EPG = results[i].EPG;
                    Subnet = results[i].Subnet;
                    Locality = results[i].Locality;
                    if (results[i].Scope.includes('S')) {
                        var Security = '<span class="glyphicon glyphicon-ok-circle" title="External Subnets for External EPGs"></span>'
                    }
                    else {
                        var Security = ''
                    }
                    if (results[i].Scope.includes('I')) {
                        var Import = '<span class="glyphicon glyphicon-ok-circle" title="Import route control"></span>'
                    }
                    else {
                        var Import = ''
                    }
                    if (results[i].Scope.includes('E')) {
                        var Export = '<span class="glyphicon glyphicon-ok-circle" title="Export route control"></span>'
                    }
                    else {
                        var Export = ''
                    }
                    var tr = document.createElement("TR");
                    var TABLE_TR = 'TABLE_TR' + i
                    tr.setAttribute("id", TABLE_TR);
                    document.getElementById("result_table").appendChild(tr);
                    var search_results = [Location, Tenant, AppProfile, EPG, Subnet, Security, Import, Export, Locality]
                    search_results.forEach(function(items) {
                        var td = document.createElement("TD");
                        td.setAttribute("style", "text-align: center; vertical-align: middle;");
                        td.innerHTML = items;
                        document.body.appendChild(td);
                        document.getElementById(TABLE_TR).appendChild(td);
                    });}
                $('#endpoint_table').DataTable({
                    retrieve: true,
                    responsive: true,
                    "language": {
                        "search": "Filter records:"
                    },
                } );
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
