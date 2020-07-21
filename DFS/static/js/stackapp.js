function unpack(data, key) {
    return data.map(function(row) { return row[key]; });
}


function getCountrydata(chosenCountry) {
    currentGdp = [];
    currentYear = [];
    for (var i = 0 ; i < qb_names.length ; i++){
        if ( qb_names[i] === chosenCountry ) {
            currentGdp.push(allGdp[i]);
            currentYear.push(allYear[i]);
        }
    }
};

function selectPlayer(){
    console.log(this)
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

    qbCount = 0 
 
    d3.selectAll('.qbOpt').on('click', function() {
        if (qbCount < 1) {
        current = d3.select('#currentSelection')
        var qbList = current.append('ul')
                .classed('list-group', true)
        var item = qbList.append('li')
                .classed('list-group-item py-0', true)
                .append('div').classed('input-group', true)
                .append('input', 'button')
                    .attr('placeholder', this.value)
                    .attr('type', 'text')
                    .property('disabled', true)
                .append('div')
                    .classed("input-group-append", true)
                    .append('span')
                        .classed('glyphicon glyphicon-remove', true)
        qbCount++;
    }
        // else if (qbCount < 1) {
        //     flash message 'enough QBs selected'
        // }
})


        

    function getCountrydata(chosenCountry) {
        currentGdp = [];
        currentYear = [];
        for (var i = 0 ; i < qb_names.length ; i++){
            if ( qb_names[i] === chosenCountry ) {
                currentGdp.push(allGdp[i]);
                currentYear.push(allYear[i]);
            }
        }
    };

    function setBubblePlot(chosenCountry) {
        getCountrydata(chosenCountry);

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

    // var innerContainer = document.querySelector('[data-num="0"'),
    //     plotEl = innerContainer.querySelector('.plot'),
    //     countrySelector = innerContainer.querySelector('.countrydata');



    // assignOptions(qb_names, countrySelector);

    // function updateCountry(){
    //     setBubblePlot(countrySelector.value);
    // }

    // countrySelector.addEventListener('change', updateCountry, false);

});