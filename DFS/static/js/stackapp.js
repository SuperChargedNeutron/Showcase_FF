function addPlayerTag(appendee, obj){
    // might be beter if i name it update player lists
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
    
        }

function updateRemoveButtonFunction(counts, currentTeam) {
    killButtonz = d3.selectAll('.rmButton')
        .on('click', function () {
            if (this.parentNode.parentNode.id == 'qbList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam[0].players.indexOf(playerText)
                currentTeam[0].players.pop(playerIndex)
                player.remove()
                counts['qbCount']--;
            } else if (this.parentNode.parentNode.id == 'rbList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam[1].players.indexOf(playerText)
                currentTeam[1].players.pop(playerIndex)
                player.remove()
                counts['rbCount']--;
            } else if (this.parentNode.parentNode.id == 'wrList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam[2].players.indexOf(playerText)
                currentTeam[2].players.pop(playerIndex)
                player.remove()
                counts['wrCount']--;
            } else if (this.parentNode.parentNode.id == 'teList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam[3].players.indexOf(playerText)
                currentTeam[3].players.pop(playerIndex)
                player.remove()
                counts['teCount']--;
            } else if (this.parentNode.parentNode.id == 'dstList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam[4].players.indexOf(playerText)
                currentTeam[4].players.pop(playerIndex)
                player.remove()
                counts['dstCount']--;
            } else if (this.parentNode.parentNode.id == 'flexList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam[5].players.indexOf(playerText)
                currentTeam[5].players.pop(playerIndex)
                player.remove()
                counts['flexCount']--;
            };
            
        })
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
function assignFlexOptions(playerNames, position) {
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

    var counts = {'qbCount' : 0,
    'rbCount' : 0,
    'wrCount' : 0,
    'teCount' : 0,
    'dstCount' : 0,
    'flexCount' : 0},
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
        if (counts['qbCount'] < 1) {
            currentTeam[0].players.push(this.value)
            var list = d3.select('#qbList')
            addPlayerTag(list, currentTeam[0])
            counts['qbCount']++;
            updateRemoveButtonFunction(counts, currentTeam)
            setPlot(currentTeam)
            
    }
        // else if (qbCount >= 1) {
        //     flash message 'enough QBs selected'
        // }
})
    d3.selectAll('.rbOpt').on('click', function() {
        if (counts['rbCount'] < 2) {
            currentTeam[1].players.push(this.value)
            var list = d3.select('#rbList')
            addPlayerTag(list, currentTeam[1]);
            counts['rbCount']++;
            updateRemoveButtonFunction(counts, currentTeam)
            
    }
    })
    d3.selectAll('.wrOpt').on('click', function() {
        if (counts['wrCount'] < 3) {
            currentTeam[2].players.push(this.value)
            var list = d3.select('#wrList')
            addPlayerTag(list, currentTeam[2]);
            counts['wrCount']++;
            updateRemoveButtonFunction(counts, currentTeam)
    }
    })
    d3.selectAll('.teOpt').on('click', function() {
        if (counts['teCount'] < 1) {
            currentTeam[3].players.push(this.value)
            var list = d3.select('#teList')
            addPlayerTag(list, currentTeam[3]);
            counts['teCount']++;
            updateRemoveButtonFunction(counts, currentTeam)
            
    }
    })
    d3.selectAll('.dstOpt').on('click', function() {
        if (counts['dstCount'] < 1) {
            currentTeam[4].players.push(this.value)
            var list = d3.select('#dstList')
            addPlayerTag(list, currentTeam[4]);
            counts['dstCount']++;
            updateRemoveButtonFunction(counts, currentTeam)
    }
    })




        

  

    function setPlot(chosenCountry) {
        
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