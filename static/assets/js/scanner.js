$(function () {
    $('#topNav .nav-link').each(function () {
        var current = '{{ request.get_full_path | urlencode }}'
        if (current == $(this).attr('href')) {
            $(this).parent().addClass('active')
        }
    })
    $('#scanner-link').click(function () {
        uni_modal("Shelter Scan", $(this).attr('data_url'))
    })
})