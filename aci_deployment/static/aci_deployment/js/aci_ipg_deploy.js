var frm = $('#ipgs');
var rslt = $('#ipg_result');
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
            get_validation_task_info(data.task_id, data.location, data.ipg_list);
        }
        },
    error: function (data) {
        document.getElementById("resultdiv").style.visibility = "hidden";
        console.log("Something went wrong!");
    }
});
return false;
});

function get_validation_task_info(task_id, location, ipg_list) {
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
                rslt.html('Validating data structure...');
            }
            else if (data.state == 'SUCCESS') {
                <!-- Clear Old  Data -->
                document.getElementById("loader").style.display = "none";
                document.getElementById("ipg_deployment_results").innerHTML = "";
                document.getElementById("resultdiv").style.visibility = "visible";
                var results = data.result[0];
                console.log(results)
                var result_location = document.getElementById("ipg_deployment_results")
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
                    if (results[i].ValidationSuccess) {
                        var br = document.createElement("br");
                        var validation_success = document.createElement("dt");
                        validation_success.setAttribute("class", "text-success");
                        result_location.appendChild(br);
                        result_location.appendChild(validation_success);
                        validation_success.innerHTML = results[i].ValidationSuccess;
                    }
                    if ("Errors" in results[i]) {
                        var validation_error = true
                    }
                }
                if (validation_error){
                    var br = document.createElement("br");
                    var validation_error = document.createElement("dt");
                    validation_error.setAttribute("class", "text-danger");
                    result_location.appendChild(br);
                    result_location.appendChild(validation_error);
                    validation_error.innerHTML = "Errors found. Please fix and try again.";
                }
                if (!validation_error){
                    document.getElementById("deploy_btn").style.visibility = "visible";
                    document.getElementById("new_file_btn").style.visibility = "visible";
                    document.getElementById("upload_btn").style.visibility = "hidden";
                    document.getElementById("location").disabled = true;
                    document.getElementById("file").disabled = true;
                    deploy_configuration(location, ipg_list);
                }
            }
            if (data.state != 'SUCCESS') {
                setTimeout(function () {
                    get_validation_task_info(task_id, location, ipg_list)
                }, 1000);
            }},
        error: function (data) {
            document.getElementById("loader").style.display = "none";
            document.getElementById("resultdiv").style.visibility = "hidden";
            rslt.html("Something went wrong!");success()
        }
    });
}