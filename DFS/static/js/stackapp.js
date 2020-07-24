function addPlayerTag(appendee, obj){
    appendee.html('')
    appendee.selectAll('li')
                .data(obj.players).enter()
                .append('li')
                .classed('list-group-item py-0', true)
                .text(function(d) { return d; })
                .append('button')
                // .attr('type', 'button')
                .classed(`${obj.position} rmButton`, true)
                .classed('btn btn-outline-danger btn-circle btn-sm', true)
                .append('svg')
                .attr('viewBox', "0 0 24 24").attr('width', "16")
                .attr('height', "16")
                .append('path') 
                .attr('fill-rule', "evenodd")
                .attr('d', "M5.72 5.72a.75.75 0 011.06 0L12 10.94l5.22-5.22a.75.75 0 111.06 1.06L13.06 12l5.22 5.22a.75.75 0 11-1.06 1.06L12 13.06l-5.22 5.22a.75.75 0 01-1.06-1.06L10.94 12 5.72 6.78a.75.75 0 010-1.06z")
    updateRemoveButtonFunction()
    
        }

function updateRemoveButtonFunction() {
    killButtonz = d3.selectAll('.rmButton')
        .on('click', removePlayer)
    return killButtonz
}

function removePlayer() {
    console.log(this.parentNode.value)
}
function assignOptions(playerNames, position) {

    d3.select(`#${position}Selection`)
        .selectAll('option')
        .data(playerNames).enter()
        .append('option')
        .attr('value', function(d) { return d.Name; })
        .classed(`${position}Opt`, true)
        .text(function(d) { return d.Name; })


}
    // callback function
    function clickPrint() {
        console.log( this );
    }

Plotly.d3.json('/stack_app_data', function(err, rows){


    var positions = ['qb', 'rb', 'wr', 'te', 'dst'],
        qbs = rows['QB']
        rbs = rows['RB'],
        wrs = rows['WR'],
        tes = rows['TE'],
        dst = rows['DST'],

    assignOptions(qbs, 'qb')
    assignOptions(rbs, 'rb')
    assignOptions(wrs, 'wr')
    assignOptions(tes, 'te')
    assignOptions(dst, 'dst')

    var qbCount = 0,
    rbCount = 0,
    wrCount = 0,
    teCount =0,
    dstCount = 0,
    flexCount = 0,
    currentTeam = [{'position' : 'QBs', 'players' : []},
                    {'position' : 'RBs', 'players' : []},
                    {'position' :'WRs', 'players' : []},
                    {'position' :'TEs', 'players' : []},
                    {'position' :'DSTs', 'players' : []}];


    var current = d3.select('#currentSelection')
                        .selectAll('ul')
                        .data(positions).enter()
                        .append('div')
                        .append('ul')
                        .classed('list-group', true)
                        .classed('positionList', true)
                        .attr('id', function(d) { return `${d}List`; })

    d3.selectAll('.qbOpt').on('click', function() {
        if (qbCount < 1) {
            currentTeam[0].players.push(this.value)
            var list = d3.select('#qbList')
            addPlayerTag(list, currentTeam[0])
            qbCount++;
    }
        // else if (qbCount >= 1) {
        //     flash message 'enough QBs selected'
        // }
})
    d3.selectAll('.rbOpt').on('click', function() {
        if (rbCount < 2) {
            currentTeam[1].players.push(this.value)
            var list = d3.select('#rbList')
            addPlayerTag(list, currentTeam[1]);
            rbCount++;
    }
    })
    d3.selectAll('.wrOpt').on('click', function() {
        if (wrCount < 3) {
            currentTeam[2].players.push(this.value)
            var list = d3.select('#wrList')
            addPlayerTag(list, currentTeam[2]);
            wrCount++;
    }

    })
    d3.selectAll('.teOpt').on('click', function() {
        if (teCount < 1) {
            currentTeam[3].players.push(this.value)
            var list = d3.select('#teList')
            addPlayerTag(list, currentTeam[3]);
            teCount++;
    }
    })
    d3.selectAll('.dstOpt').on('click', function() {
        if (dstCount < 1) {
            currentTeam[4].players.push(this.value)
            var list = d3.select('#dstList')
            addPlayerTag(list, currentTeam[4]);
            dstCount++;
    }
    })




        

  

    function setBubblePlot(chosenCountry) {
        
        var trace1 = {
            x: [1,2,3],
            y: [1,2,3],
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