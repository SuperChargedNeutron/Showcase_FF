function makeVariables(amnt, cols) {
    var len = parseInt(amnt.attr('value'))

    var variables = d3.select('#variableInput');
    
    for (i = 1; i < len + 1; i++) {
        inputDiv = variables.append('div').classed('input-group', true)
        weightInput = inputDiv.append('input')
                        .classed('form-control', true)
                        .attr('type', 'text')
                        .attr('id', `weight${i}`)
        columnSelect = inputDiv.append('select').classed('custom-select colSelect', true)
                        .attr('id', `column${i}`)
                        .selectAll('option')
                        .data(cols).enter()
                        .append('option')
                        .attr('value', (d) => d)
                        .text((d) => d)
    }
}


function usePosition(url) {
    d3.json(url).then(function(data) {
        var weightInputs = [];
        var colInputs = [];
        var columns = Object.keys(data[0])
        var amnt = d3.select('#amnt')
        makeVariables(amnt, columns)

        var submitButton = d3.select('#forButton')
                .append('button')
                .attr('type', 'button')
                .classed('btn btn-primary', true)
                .text('Submit')

        
        d3.selectAll('.colSelect').on('input', function() {
            var colObject = {},
            colId = this.id,
            colValue = this.value,
            index = colId.charAt(colId.length - 1) - 1;
            colObject[colId] = colValue;
            colInputs.splice(index, 1, colObject)
            console.log(colInputs)
        })
        d3.selectAll('.form-control').on('input', function() {
            var weightObject = {},
            weightid = this.id,
            weightvalue = this.value,
            index = weightid.charAt(weightid.length - 1) - 1;
            console.log(weightid)
            weightObject[weightid] = weightvalue
            weightInputs.splice(index, 1, weightObject)
            
        })

        submitButton.on('click', e => {
            var name = d3.select('#metaLabel').text().substring(8),
            encodedPointMetadata = encodeURI(JSON.stringify({
                'pos': d3.select('#metaPosition').text().substring(11), 
                'week': d3.select('#metaWeek').text().substring(7), 
                'season': d3.select('#metaSeason').text().substring(9)}))
            encodedName = encodeURI(name),
            encodedColumnDict = encodeURI(JSON.stringify(colInputs)),
            encodedWeightDict = encodeURI(JSON.stringify(weightInputs));
            window.location.assign(`/${encodedName}/${encodedPointMetadata}/${encodedWeightDict}/${encodedColumnDict}`)            
        })
    })
}

var pos = d3.select('#metaPosition').attr('value')
usePosition(`/${pos}_data`)