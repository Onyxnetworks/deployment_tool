var frm = $('#contract_search');
var rslt = $('#contract_results');


frm.submit(function () {
    document.getElementById("tablediv").style.visibility = "hidden";
    $.ajax({
        type: frm.attr('method'),
        url: frm.attr('action'),
        data: frm.serialize(),
        success: function (data) {
            if (data.task_id != null) {
                get_task_info(data.task_id);
            }
        },
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
                    rslt.html('Searching Contracts...');
                }
                else if (data.state == 'SUCCESS') {
                    console.log('Success')
                    document.getElementById("loader").style.display = "none";
                    document.getElementById("result_table").innerHTML = "";
                    document.getElementById("tablediv").style.visibility = "visible";
                    var results = data.result;
                    console.log(results);
                }

                if (data.state != 'SUCCESS') {
                    setTimeout(function () {
                        get_task_info(task_id)
                    }, 1000);
                }
            },

            error: function (data) {
                document.getElementById("tablediv").style.visibility = "hidden";
                document.getElementById("loader").style.display = "none";
                rslt.html("Something went wrong!");
                success()
            }
        },
    );
}