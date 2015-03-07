$(function() {
    $('#new-task-deadline').datetimepicker({
        format: 'YYYY-MM-DD HH:mm',
        defaultDate: moment().format("YYYY-MM-DD HH:mm")
    });
    $('.task-deadline').blur(function() {
        var timestamp = Date.parse($(this).val());
        $(this).parent().find('input[name="deadline"]').val(timestamp);
    });
});

$(function() {
    var getCookie = function(name) {
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    };

    // RESTful API
    $('.restful').on('click', function() {
        var httpMethod = $(this).data('method');
        var dataId = $(this).data('id');
        var url = $(this).data('action');
        var xsrf_cookie = getCookie('_xsrf');
        $.ajax({
            url: url,
            data: {id: dataId, _xsrf:xsrf_cookie},
            method: httpMethod,
            success: function(data) {
                window.location.reload();
            },
            error: function() {
                window.location.reload();
            }
        });
    });

    // Modify task
    $('#modify-task-modal').on('show.bs.modal', function(e) {
        // get the data of task
        var task = $(e.relatedTarget);
        var modal = $(e.currentTarget);
        var taskId = task.data('task-id');
        var taskTitle = task.data('task-title');
        var taskDescription = task.data('task-description');
        var taskDeadline = task.data('task-deadline');

        //populate the textbox
        modal.find('input[name="id"]').val(taskId);
        modal.find('input[name="title"]').val(taskTitle);
        modal.find('input[name="description"]').val(taskDescription);
        modal.find('input[name="deadline"]').val(taskDeadline);
        var picker = $('#modify-task-deadline').data('DateTimePicker');
        if(picker) {
            picker.date(moment(taskDeadline).format("YYYY-MM-DD HH:mm"));
        } else {
            $('#modify-task-deadline').datetimepicker({
                format: "YYYY-MM-DD HH:mm",
                defaultDate: moment(taskDeadline).format("YYYY-MM-DD HH:mm")
            });
        }
    });

    // RESTful API for modifing task
    $('#modify-task-form').submit(function() {
        var data = $(this).serializeArray();
        var url = $(this).attr('action');
        var httpMethod = $(this).attr('method');
        var xsrf_cookie = getCookie('_xsrf');
        $.ajax({
            url: url,
            data: data,
            method: 'PUT',
            success: function() {
                window.location.reload();
            },
            error: function() {
                window.location.reload();
            }
        });
        return false;
    });
}());
