function getData(url){
    var colSelect = d3.select('#colSelect')
    var tableHeader = d3.select('#myTable').append('thead').append('tr')
    // var tableFooter = d3.select('#myTable').append('tfoot').append('tf').append('tr')


    d3.json(url).then((data) => {
        cols = []
        
        data.forEach(obj => Object.keys(obj).map( function(key) {
            if (!cols.includes(key)) {
                cols.push(key)
            }
        })
        )


        colSelect.selectAll('option')
            .data(cols).enter()
            .append('option')
            .classed('toggle-vis', true)
            .attr("data-column", (d,i) => i)
            .attr('id', (d) => d)
            .text((d) => d);
 
        tableHeader.selectAll('th')
            .data(cols).enter()
            .append('th')
            .text((d) => `${d}`);
        // tableFooter.selectAll('th')
        //     .data(cols).enter()
        //     .append('th')
        //     .text((d) => `${d}`);

        colObjects = cols.map(function(val){ 
        return {'data':val} ; 
    })

    var table = $('#myTable').DataTable( {
        "scrollX": true,
        dom: 'BRSlfrtip',
        "lengthChange": true,
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
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
                    columns: ':visible'
                }
            },

            // 'colvis'
        ],
        colReorder: true,
        select: {
                style:    'os',
                selector: 'td:first-child',
                blurable: true
            },
        data: data,
        columns : colObjects
        } );

 
        $('.toggle-vis').on('click', function (e) {
            e.preventDefault();
            // Get the column API object
            var column = table.column( $(this).attr('data-column') );     
            // Toggle the visibility
            column.visible( ! column.visible() );
        } );
        // initial toggle
        $(function() {
            initColumns = ['name',
            'Team', 
            'Opp', 
            'Price', 
            'Value', 
            'aFPA', 
            'dk_50_percentile',
            'dk_75_percentile',
            'dk_85_percentile',
            'dk_95_percentile',
            'dk_99_percentile',
            'Projection',//this is SS projection 
            'DK_Proj',
            'DK_Flr',	
            'DK_Ceil',]
            // '4f4 RZ L3',
            // 'Air Tar L3',
            // Avgs,
            // JALG]
            d3.selectAll('.toggle-vis')
                .each(function(d) {
                    if (!initColumns.includes(d)) {
                        var column = table.column($(this).attr('data-column') );
                        column.visible( ! column.visible() );
                    }
            })

            $('#myTable tbody').on( 'click', 'tr', function () {
                if ( $(this).hasClass('selected') ) {
                    $(this).removeClass('selected');
                }
                else {
                    table.$('tr.selected').removeClass('selected');
                    $(this).addClass('selected');
                }
            } );
         
            $('#deleteButton').click( function () {
                table.row('.selected').remove().draw( false );
            } );
        });

    
}
);
}
var pos = d3.select('.h1').attr('id')
url = `${pos}_data`
getData(url)