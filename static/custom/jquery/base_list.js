$(document).ready(function(){
    $('.table-hover tbody tr').css('cursor', 'pointer').on('click', function() {
        window.location = $(this).attr('data-href');
    });
})

