var frm = $('#contracts');
var rslt = $('#contract_result');
frm.submit(function(e) {e.preventDefault();
var formData = new FormData(this);
document.getElementById("resultdiv").style.visibility = "hidden";
$.ajax({
    type: 'post',
    url: frm.attr('action'),
    data: formData,
    cache: false,
    processData: false,
    contentType: false,
    success: function (data) {
        if (data.task_id != null) {
            get_validation_task_info(data.task_id, data.location, data.rule_list);
        }
        },
    error: function (data) {
        document.getElementById("resultdiv").style.visibility = "hidden";
        console.log("Something went wrong!");
    }
});
return false;
});
function get_validation_task_info(task_id, location, rule_list) {
    $.ajax({
        type: 'get',
        url: '/get_task_info/',
        data: {'task_id': task_id},
        success: function (data) {
            rslt.html('');
            if (data.state == 'PENDING') {
                rslt.html('Validating data structure...');
            }
            else if (data.state == 'SUCCESS') {
                <!-- Clear Old  Data -->
                document.getElementById("contract_deployment_results").innerHTML = "";
                document.getElementById("resultdiv").style.visibility = "visible";
                var results = data.result;
                var result_location = document.getElementById("contract_deployment_results")
                var validation_error = false;
                for (i = 0, len = results.length, text = ""; i < len; i++) {
                    if (results[i].Notifications) {
                        var p_not = document.createElement("p");
                        result_location.appendChild(p_not);
                        p_not.innerHTML = results[i].Notifications;
                    }
                    if (results[i].Errors) {
                        var p_err = document.createElement("p");
                        result_location.appendChild(p_err);
                        p_err.innerHTML = results[i].Errors;
                    }
                    if ("Errors" in results[i]) {
                        var validation_error = true
                    }
                }
                if (validation_error){
                    var p_error = document.createElement("p");
                    result_location.appendChild(p_error);
                    p_error.innerHTML = "Errors found. Please fix and try again.";
                }
                if (!validation_error){
                    document.getElementById("deploy_btn").style.visibility = "visible";
                    document.getElementById("new_file_btn").style.visibility = "visible";
                    document.getElementById("upload_btn").style.visibility = "hidden";
                    document.getElementById("location").disabled = true;
                    document.getElementById("file").disabled = true;
                    deploy_configuration(location, rule_list);
                }
            }
            if (data.state != 'SUCCESS') {
                setTimeout(function () {
                    get_validation_task_info(task_id, location, rule_list)
                }, 1000);
            }},
        error: function (data) {
            document.getElementById("resultdiv").style.visibility = "hidden";
            rslt.html("Something went wrong!");success()
        }
    });
}
function deploy_configuration(location, rule_list) {
    $("#deploy_btn").click(function(){
        var raw_json = {'location': location, 'rule_list': rule_list};
        post_data = JSON.stringify({'location': location, 'rule_list': rule_list});
        $.ajax({
            type: 'post',
            url: '/aci/contract_deployment_push/',
            data: post_data,
            dataType: 'json',
            contentType: 'application/json',
            success: function (data) {
                if (data.task_id != null) {
                    get_deployment_task_info(data.task_id);
                }},
            error: function (data) {
                document.getElementById("tablediv").style.visibility = "hidden";
                console.log("Something went wrong!");
            }
        });
    });
}
function get_deployment_task_info(task_id) {$.ajax({
    type: 'get',
    url: '/get_task_info/',
    data: {'task_id': task_id},
    success: function (data) {
        rslt.html('');
        if (data.state == 'PENDING') {
            rslt.html('Pushing configuration to APIC...');
            document.getElementById("resultdiv").style.visibility = "hidden";
            document.getElementById("contract_deployment_results").innerHTML = "";
        }
        else if (data.state == 'SUCCESS') {
            <!-- Clear Old  Data -->
            document.getElementById("contract_deployment_results").innerHTML = "";
            document.getElementById("resultdiv").style.visibility = "visible";
            var results = data.result;
            var result_location = document.getElementById("contract_deployment_results")
            var validation_error = false;
            for (i = 0, len = results.length, text = ""; i < len; i++) {

                if (results[i].Headers) {
                    var header_id = 'header_id_' + i;
                    var header = document.createElement("dt");
                    header.setAttribute("id", header_id);
                    result_location.appendChild(header);
                    header.innerHTML = results[i].Headers;
                }
                if (results[i].Notifications) {
                    var notifications = document.createElement("dd");
                    document.getElementById(header_id).appendChild(notifications);
                    notifications.innerHTML = results[i].Notifications;
                }
                if (results[i].Errors) {
                    var errors = document.createElement("dd");
                    document.getElementById(header_id).appendChild(errors);
                    notifications.innerHTML = results[i].Errors;

                }
                if ("Errors" in results[i]) {
                    var validation_error = true
                }
            }
        }
        if (data.state != 'SUCCESS') {
            setTimeout(function () {
                get_deployment_task_info(task_id)
            }, 1000);
        }},
    error: function (data) {
        document.getElementById("tablediv").style.visibility = "hidden";
        rslt.html("Something went wrong!");success()
    }
})
}