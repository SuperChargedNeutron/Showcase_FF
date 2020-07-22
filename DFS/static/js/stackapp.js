function unpack(data, key) {
    return data.map(function(row) { return row[key]; });
}

function addPlayerTag(appendee, name){
    var listButton = appendee.append('li')
                .classed('list-group-item py-0', true)
                .text(`${name}    `)
                .append('button')
                .attr('type', 'button')
                .attr('id', 'removeButton')
                .classed('btn btn-outline-danger btn-circle btn-sm', true)
                .append('svg')
                .attr('viewBox', "0 0 24 24").attr('width', "16")
                .attr('height', "16")
                .append('path') 
                .attr('fill-rule', "evenodd")
                .attr('d', "M5.72 5.72a.75.75 0 011.06 0L12 10.94l5.22-5.22a.75.75 0 111.06 1.06L13.06 12l5.22 5.22a.75.75 0 11-1.06 1.06L12 13.06l-5.22 5.22a.75.75 0 01-1.06-1.06L10.94 12 5.72 6.78a.75.75 0 010-1.06z")
                
        
        return listButton
            }

function assignOptions(playerNames, position) {

    var selector = d3.select(`#${position}Selection`)
    playerNames.forEach(name => {
        selector.append('option')
            .attr('value', name)
            .classed(`${position}Opt`, true)
            .text(name)
    })

}
    // callback function
    function clickPrint() {
        console.log( this );
    }
Plotly.d3.json('/stack_app_data', function(err, rows){


    var qbs = rows['QB']
        rbs = rows['RB'],
        wrs = rows['WR'],
        tes = rows['TE'],
        dst = rows['DST'],
        qb_names = unpack(qbs, 'Name'),
        rb_names = unpack(rbs, 'Name'),
        wr_names = unpack(wrs, 'Name'),
        te_names = unpack(tes, 'Name'),
        dst_names = unpack(dst, 'Name')

    assignOptions(qb_names, 'qb')
    assignOptions(rb_names, 'rb')
    assignOptions(wr_names, 'wr')
    assignOptions(te_names, 'te')
    assignOptions(dst_names, 'dst')

    var qbCount = 0,
    rbCount = 0,
    wrCount = 0,
    teCount =0,
    dstCount = 0,
    flexCount = 0;

    d3.selectAll('.qbOpt').on('click', function() {
        console.log(qbCount)
        if (qbCount < 1) {
        current = d3.select('#currentSelection')
        var div = current.append('div')
                .append('ul')
                .classed('list-group', true)
        addPlayerTag(div, this.value)
        qbCount++;
    }
        // else if (qbCount >= 1) {
        //     flash message 'enough QBs selected'
        // }
})
    d3.selectAll('.rbOpt').on('click', function() {
        if (rbCount < 1) {
        current = d3.select('#currentSelection');
        var div = current.append('div')
                .append('ul')
                .attr('id', 'rbList')
                .classed('list-group', true);
        addPlayerTag(div, this.value);
        rbCount++;
    }
    else if (rbCount < 2) {
        var list = d3.select('#rbList')
        addPlayerTag(list, this.value)
        rbCount++;
        // else if (qbCount >= 1) {
        //     flash message 'enough QBs selected'
        // }
    }
    }
    )
    d3.selectAll('.wrOpt').on('click', function() {
        if (wrCount < 1) {
        current = d3.select('#currentSelection');
        var div = current.append('div')
                .append('ul')
                .attr('id', 'wrList')
                .classed('list-group', true);
        addPlayerTag(div, this.value);
        wrCount++;
    }
    else if (wrCount < 3) {
        var list = d3.select('#wrList')
        addPlayerTag(list, this.value)
        wrCount++;
        // else if (qbCount >= 1) {
        //     flash message 'enough QBs selected'
        // }
    }
    })
    d3.selectAll('.teOpt').on('click', function() {
        if (teCount < 1) {
        current = d3.select('#currentSelection');
        var div = current.append('div')
                .append('ul')
                .attr('id', 'teList')
                .classed('list-group', true);
        addPlayerTag(div, this.value);
        teCount++;
    }
    })
    d3.selectAll('.dstOpt').on('click', function() {
        if (dstCount < 1) {
        current = d3.select('#currentSelection');
        var div = current.append('div')
                .append('ul')
                .attr('id', 'dstList')
                .classed('list-group', true);
        addPlayerTag(div, this.value);
        dstCount++;
    }
    })
    d3.selectAll('#removeButton').each(function() {
        d3.select(this).on('click', clickPrint)
        
        console.log(d3.select(this))
        console.log(this)
    })

        

  

    function setBubblePlot(chosenCountry) {
        
        var trace1 = {
            x: unpack(qbs, 'Price'),
            y: unpack(qbs, 'Projection'),
            mode: 'markers',
            marker: {
                size: 12,
                opacity: 0.5
            }
        };

        var data = [trace1];

        var layout = {
            title:'Line and Scatter Plot',
            height: 440,
            width: 700
        };

        Plotly.newPlot('stackApp', data, layout);
    };


});