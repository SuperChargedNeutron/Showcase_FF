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
        dst_names = unpack(dst, 'Name'),

        console.log(qb_names);
        

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

    // Default Country data
    setBubblePlot('Afghanistan');

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
            height: 400,
            width: 480
        };

        Plotly.newPlot('stackApp', data, layout);
    };

    var innerContainer = document.querySelector('[data-num="0"'),
        plotEl = innerContainer.querySelector('.plot'),
        countrySelector = innerContainer.querySelector('.countrydata');

    function assignOptions(textArray, selector) {
        for (var i = 0; i < textArray.length;  i++) {
            var currentOption = document.createElement('option');
            currentOption.text = textArray[i];
            selector.appendChild(currentOption);
        }
    }

    assignOptions(qb_names, countrySelector);

    function updateCountry(){
        setBubblePlot(countrySelector.value);
    }

    countrySelector.addEventListener('change', updateCountry, false);
});