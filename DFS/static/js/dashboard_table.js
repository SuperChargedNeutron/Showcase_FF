function getData(url, defaultCols){
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
            d3.selectAll('.toggle-vis')
                .each(function(d) {
                    if (!defaultCols.includes(d)) {
                        var column = table.column($(this).attr('data-column') );
                        column.visible( ! column.visible() );
                    }
            })
            d3.selectAll('.toggle-vis')
                .each(function(d) {
                    if (d.startsWith('w')) {
                        var column = table.column($(this).attr('data-column') );
                        column.visible(true);
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
var thresh = d3.select('#thresh').text()

if (pos == 'QB') {
    cols = qb_cols
} else if (pos == 'RB') {
    cols = rb_cols
} else if (pos == 'WR') {
    cols = wr_cols
} else if (pos = 'TE') {
    cols = te_cols
} else if (pos = 'DST') {
    cols = def_cols
};

if (thresh != '') {
    url = `/${pos}_data/${thresh}`
}

else if (thresh == '') {
    url = `/${pos}_data`
}

console.log(url)
getData(url, cols)