var frm = $('#external_epg');
var rslt = $('#externnal_epg_result');
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
                document.getElementById("epg_deployment_results").innerHTML = "";
                document.getElementById("resultdiv").style.visibility = "visible";
                var results = data.result;
                var result_location = document.getElementById("epg_deployment_results")
                var validation_error = false;
                for (i = 0, len = results.length, text = ""; i < len; i++) {
                    if (results[i].Headers) {
                        var br = document.createElement("br");
                        var header = document.createElement("dt");
                        result_location.appendChild(br);
                        result_location.appendChild(header);
                        header.innerHTML = results[i].Headers;
                    }
                    if (results[i].Headers2) {
                        var header2 = document.createElement("dt");
                        header2.setAttribute("class", "text-muted");
                        header2.setAttribute("style", "text-indent: 15px");
                        result_location.appendChild(header2);
                        header2.innerHTML = results[i].Headers2;
                    }
                    if (results[i].Notifications) {
                        var notifications = document.createElement("dd");
                        notifications.setAttribute("style", "text-indent: 30px");
                        result_location.appendChild(notifications);
                        notifications.innerHTML = results[i].Notifications;
                    }
                    if (results[i].NotificationsInfo) {
                        var notifications_info = document.createElement("dd");
                        notifications_info.setAttribute("style", "text-indent: 30px");
                        notifications_info.setAttribute("class", "text-info");
                        result_location.appendChild(notifications_info);
                        notifications_info.innerHTML = results[i].NotificationsInfo;
                    }
                    if (results[i].NotificationsSuccess) {
                        var notifications_success = document.createElement("dd");
                        notifications_success.setAttribute("style", "text-indent: 30px");
                        notifications_success.setAttribute("class", "text-success");
                        result_location.appendChild(notifications_success);
                        notifications_success.innerHTML = results[i].NotificationsSuccess;
                    }
                    if (results[i].NotificationsWarning) {
                        var notifications_warning = document.createElement("dd");
                        notifications_warning.setAttribute("style", "text-indent: 30px");
                        notifications_warning.setAttribute("class", "text-warning");
                        result_location.appendChild(notifications_warning);
                        notifications_warning.innerHTML = results[i].NotificationsWarning;
                    }
                    if (results[i].Errors) {
                        var errors = document.createElement("dd");
                        errors.setAttribute("class", "text-danger");
                        errors.setAttribute("style", "text-indent: 30px");
                        result_location.appendChild(errors);
                        errors.innerHTML = results[i].Errors;
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
        post_data = JSON.stringify({'location': location, 'rule_list': rule_list});
        $.ajax({
            type: 'post',
            url: '/aci/external_epg_deployment_push/',
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
            document.getElementById("epg_deployment_results").innerHTML = "";
        }
        else if (data.state == 'SUCCESS') {
            <!-- Clear Old  Data -->
            document.getElementById("epg_deployment_results").innerHTML = "";
            document.getElementById("resultdiv").style.visibility = "visible";
            var results = data.result;
            var result_location = document.getElementById("epg_deployment_results")
            var validation_error = false;
            for (i = 0, len = results.length, text = ""; i < len; i++) {
                if (results[i].Headers) {
                    var br = document.createElement("br");
                    var header = document.createElement("dt");
                    result_location.appendChild(br);
                    result_location.appendChild(header);
                    header.innerHTML = results[i].Headers;
                }
                if (results[i].Headers2) {
                    var header2 = document.createElement("dt");
                    header2.setAttribute("class", "text-muted");
                    header2.setAttribute("style", "text-indent: 15px");
                    result_location.appendChild(header2);
                    header2.innerHTML = results[i].Headers2;
                }
                if (results[i].Notifications) {
                    var notifications = document.createElement("dd");
                    notifications.setAttribute("style", "text-indent: 30px");
                    result_location.appendChild(notifications);
                    notifications.innerHTML = results[i].Notifications;
                }
                if (results[i].NotificationsInfo) {
                    var notifications_info = document.createElement("dd");
                    notifications_info.setAttribute("style", "text-indent: 30px");
                    notifications_info.setAttribute("class", "text-info");
                    result_location.appendChild(notifications_info);
                    notifications_info.innerHTML = results[i].NotificationsInfo;
                }
                if (results[i].NotificationsSuccess) {
                    var notifications_success = document.createElement("dd");
                    notifications_success.setAttribute("style", "text-indent: 30px");
                    notifications_success.setAttribute("class", "text-success");
                    result_location.appendChild(notifications_success);
                    notifications_success.innerHTML = results[i].NotificationsSuccess;
                }
                if (results[i].NotificationsWarning) {
                    var notifications_warning = document.createElement("dd");
                    notifications_warning.setAttribute("style", "text-indent: 30px");
                    notifications_warning.setAttribute("class", "text-warning");
                    result_location.appendChild(notifications_warning);
                    notifications_warning.innerHTML = results[i].NotificationsWarning;
                }
                if (results[i].Errors) {
                    var errors = document.createElement("dd");
                    errors.setAttribute("class", "text-danger");
                    errors.setAttribute("style", "text-indent: 30px");
                    result_location.appendChild(errors);
                    errors.innerHTML = results[i].Errors;
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
