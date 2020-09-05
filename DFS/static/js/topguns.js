$(document).ready( function () {
    $('table.topguntable').DataTable({
        "scrollY": true,
        dom: 'BRSltipr',
        "bFilter": false,
        buttons: [
            {
                extend: 'copyHtml5',
                exportOptions: {
                    columns: [ 0, ':visible' ]
                }
            },
            {
                extend: 'excelHtml5',
                exportOptions: {
                    columns: [ 0, ':visible' ]
                }
            },

            // 'colvis'
        ],
        colReorder: true
    });
} );