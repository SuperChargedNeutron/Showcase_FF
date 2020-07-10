function getData(url){
    var checklist = d3.select('#toggles')
    // var tableHeader = d3.select('#myTable').append('thead').append('th').append('tr')
    // var tableFooter = d3.select('#myTable').append('tfoot').append('tf').append('tr')


    d3.json(url).then((data) => {
        cols = []
        colObjects = []
        data.forEach(obj => Object.keys(obj).forEach( function(key) {
            if (!cols.includes(key)) {
                cols.push(key)
                colObjects.push({data : key})
            }
        })
        )


    console.log(cols)
    var i = 0;
    cols.forEach(col => {
       var litem =  checklist.append('a')
        .classed('toggle-vis', true)
        .attr("data-column", i.toString())
        .text(`${col} - `);
        i++;

        // tableHeader.append('td').text(col)
        // tableFooter.append('td').text(col)
    })
    
    var table = $('#myTable').DataTable( {
        select: true,
            data: data,
            columns : colObjects
        } );
     
        $('a.toggle-vis').on('click', function (e) {
            console.log(e);
            e.preventDefault();
     
            // Get the column API object
            var column = table.column( $(this).attr('data-column') );
     
            // Toggle the visibility
            column.visible( ! column.visible() );
        } );

    
}
);
}
var pos = d3.select('#position').html()
url = `${pos}_data`

getData(url)