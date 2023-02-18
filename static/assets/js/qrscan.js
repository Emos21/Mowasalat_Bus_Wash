const loader = $('<div>')
loader.attr('id', 'pre-loader')
loader.html('<div class="lds-default"><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div></div>')

window.start_loader = function () {
    $('body').removeClass('loading')
    if ($('#pre-loader').length > 0)
        $('#pre-loader').remove();
    $('body').append(loader)
    $('body').addClass('loading')
}
window.end_loader = function () {
    if ($('#pre-loader').length > 0)
        $('#pre-loader').remove();
    $('body').removeClass('loading')

}

window.uni_modal = function ($title = '', $url = '', $size = "") {
    start_loader()
    $.ajax({
        url: $url,
        error: err => {
            console.log()
            alert("Warning!! Fraud Qr")
            window.location.reload();
        },
        success: function (resp) {
            if (resp) {
                console.log("here 1 -------")
                $('#uni_modal .modal-title').html($title)
                $('#uni_modal .modal-body').html(resp)
                if ($size != '') {
                    $('#uni_modal .modal-dialog').addClass($size + '  modal-dialog-centered')
                } else {
                    $('#uni_modal .modal-dialog').removeAttr("class").addClass("modal-dialog modal-md modal-dialog-centered")
                }
                $('#uni_modal').modal({
                    backdrop: 'static',
                    keyboard: false,
                    focus: true
                })
                $('#uni_modal').modal('show')
                end_loader()
            }
        }
    })
}
window._conf = function ($msg = '', $func = '', $params = []) {
    $('#confirm_modal #confirm').attr('onclick', $func + "(" + $params.join(',') + ")")
    $('#confirm_modal .modal-body').html($msg)
    $('#confirm_modal').modal('show')
}

$(function () {
    $('#uni_modal').on('shown.bs.modal', function () {
        if ($('#e-details').length > 0) {
            var delete_btn = $('<button id="delete-btn" class="btn btn-danger btn-sm bg-gradient rounded-0 me-2"><i class="fa fa-trash"></i> Delete</button>')
            var edit_btn = $('<a id="edit-btn" href="" class="btn btn-primary btn-sm bg-gradient rounded-0 me-2"><i class="fa fa-edit"></i> Edit</a>')
            $(this).find('.modal-sub-footer').prepend(delete_btn)
            $(this).find('.modal-sub-footer').prepend(edit_btn)
            delete_btn.click(function () {
                _conf("Are you sure to delete this employee?", "delete_employee")
            })

            $('#uni_modal').on('hide.bs.modal', function () {
                delete_btn.remove()
                edit_btn.remove()
            })

        }
    })
})

function delete_employee() {
    start_loader()
    $.ajax({
        url: emp_delete_url,
        error: err => {
            console.error(err)
            alert("An error occurred.")
            end_loader()
        },
        success: function (resp) {
            if (resp.status == 'success') {
                location.reload()
            } else if (!!resp.msg) {
                alert(resp.msg)
            }
            end_loader()
        }
    })
}
// <-------------  Trying to refresh page if scan modal is closed      ----------------->

// $('#uni_modal').on('hidden.bs.modal', function () {
//     if (!$('#uni_modal').hasClass('no-reload')) {
//         location.reload();
//     }
// });