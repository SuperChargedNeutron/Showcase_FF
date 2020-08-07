$(document).ready( function () {
    $('#myTable').DataTable({
        "scrollX": true,
        dom: 'BRSlftipr',
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