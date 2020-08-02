function makeVariables(amnt, cols) {
    var len = parseInt(amnt.attr('value'))
    console.log(len)
    var operations = [['mult', '*'], ['div', '/'], ['plus','+'], ['minus', '-']]
    var variables = d3.select('#variableRow');
    console.log(variables)
    
    for (i = 0; i < len - 1; i++) {
        constants = variables.append('input')
        selectCol = variables.append('select')
            .selectAll('option')
            .data(cols).enter()
            .append('option')
            .attr('value', (d) => d) 
            .text((d) => d)
        ops = variables.append('select')
            .selectAll('option')
            .data(operations).enter()
            .append('option')
            .attr('value', d => d[0]) 
            .text((d) => d[1])
    }
    constants = variables.append('input')
    selectCol = variables.append('select')
        .selectAll('option')
        .data(cols).enter()
        .append('option')
        .attr('value', (d) => d) 
        .text((d) => d)
}


function usePosition(url) {
    d3.json(url).then(function(data) {
        var columns = Object.keys(data[0])
        var amnt = d3.select('#amnt')
        makeVariables(amnt, columns)

        var submitButton = d3.select('#forButton')
                .append('button')
                .attr('type', 'button')
                .classed('btn btn-primary', true)
                .text('Submit')

        submitButton.on('click', e => {
            console.log('hi')
        })
    })
}

var pos = d3.select('#position').attr('value')
usePosition(`/${pos}_data`)