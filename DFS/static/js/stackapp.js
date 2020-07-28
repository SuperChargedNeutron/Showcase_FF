function addPlayerTag(appendee, obj){
    // might be beter if i name it update player lists
    appendee.html('')
    appendee.selectAll('li')
                .data(obj).enter()
                .append('li')
                .classed('list-group-item py-0', true)
                .text(function(d) { return d; })
                .append('button')
                // .attr('type', 'button')
                .classed('rmButton', true)
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
                playerIndex = currentTeam.QBs.players.indexOf(playerText)
                currentTeam.QBs.players.pop(playerIndex)
                currentTeam.QBs.prices.pop(playerIndex)
                currentTeam.QBs.projs.pop(playerIndex)
                player.remove()
                counts['qbCount']--;
                setPlot(currentTeam)
            } else if (this.parentNode.parentNode.id == 'rbList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam.RBs.players.indexOf(playerText)
                currentTeam.RBs.players.pop(playerIndex)
                currentTeam.RBs.prices.pop(playerIndex)
                currentTeam.RBs.projs.pop(playerIndex)
                player.remove()
                counts['rbCount']--;
                setPlot(currentTeam)
            } else if (this.parentNode.parentNode.id == 'wrList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam.WRs.players.indexOf(playerText)
                currentTeam.WRs.players.pop(playerIndex)
                currentTeam.WRs.prices.pop(playerIndex)
                currentTeam.WRs.projs.pop(playerIndex)
                player.remove()
                counts['wrCount']--;
                setPlot(currentTeam)
            } else if (this.parentNode.parentNode.id == 'teList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam.TEs.players.indexOf(playerText)
                currentTeam.TEs.players.pop(playerIndex)
                currentTeam.TEs.prices.pop(playerIndex)
                currentTeam.TEs.projs.pop(playerIndex)
                player.remove()
                counts['teCount']--;
                setPlot(currentTeam)
            } else if (this.parentNode.parentNode.id == 'dstList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam.DSTs.players.indexOf(playerText)
                currentTeam.DSTs.players.pop(playerIndex)
                currentTeam.DSTs.prices.pop(playerIndex)
                currentTeam.DSTs.projs.pop(playerIndex)
                player.remove()
                counts['dstCount']--;
                setPlot(currentTeam)
            } else if (this.parentNode.parentNode.id == 'flexList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam.flexs.players.indexOf(playerText)
                currentTeam.flexs.players.pop(playerIndex)
                currentTeam.flexs.prices.pop(playerIndex)
                currentTeam.flexs.projs.pop(playerIndex)
                player.remove()
                counts['flexCount']--;
                setPlot(currentTeam)
            };
            
        })
}

function updateFlexOptions(counts, currentTeam) {
    d3.selectAll('.flexPlayerOpt').on('click', function() {
        if (counts['flexCount'] < 1) {
            currentTeam.flexs.players.push(this.value)
            var proj = d3.select(this).attr('proj')
            var price = d3.select(this).attr('price')
            currentTeam.flexs.projs.push(proj)
            currentTeam.flexs.prices.push(price)
            var list = d3.select('#flexList')
            addPlayerTag(list, currentTeam.flexs.players);
            counts['flexCount']++;
            updateRemoveButtonFunction(counts, currentTeam)
            setPlot(currentTeam)
    }
    })
}

function assignOptions(playerNames, position) {
    d3.select(`#${position}Selection`).html('')
        .selectAll('option')
        .data(playerNames).enter()
        .append('option')
        .attr('value', function(d) { 
            if (position == 'flexPosition') {
                return d; 
            } else if (position != 'flexPosition') {
                return d.Name;
            }})
        .classed(`${position}Opt`, true)
        .attr('proj', function (d) {return d.Projection})
        .attr('price', function (d) {return d.Price})
        .text(function(d) { 
            if (position == 'flexPosition') {
                return d; 
            } else if (position != 'flexPosition') {
                return d.Name;
            }})
}


function setPlot(currentTeam) {
    var prices = Object.values(currentTeam).map(position => position.prices).flat(1),
        projections = Object.values(currentTeam).map(position => position.projs).flat(1),
        names = Object.values(currentTeam).map(position => position.players).flat(1)
        prices.shift()
        projections.shift()
        names.shift()

    var trace1 = {
        x: prices,
        y: projections,
        mode: 'markers',
        text: names,
        marker: {
            size: 12,
            opacity: 0.3
        }
    };

    var data = [trace1];

    var layout = {
        title:'Stack App',
        height: 440,
        width: 700
    };

    Plotly.newPlot('stackApp', data, layout);
}

Plotly.d3.json('/stack_app_data', function(data){

    
    var playerData = data['names'],
    teams = data['teams'];


    var positions = ['qb', 'rb', 'wr', 'te', 'dst', 'flex'],
        qbs = playerData['QB']
        rbs = playerData['RB'],
        wrs = playerData['WR'],
        tes = playerData['TE'],
        dst = playerData['DST'],

    assignOptions(qbs, 'qb')
    assignOptions(rbs, 'rb')
    assignOptions(wrs, 'wr')
    assignOptions(tes, 'te')
    assignOptions(dst, 'dst')
    assignOptions(['RB', 'WR', 'TE'], 'flexPosition')

    var counts = {'qbCount' : 0,
    'rbCount' : 0,
    'wrCount' : 0,
    'teCount' : 0,
    'dstCount' : 0,
    'flexCount' : 0},
    currentTeam = { 'teamName' : '',
        'QBs' : {'players' : [], 'projs' : [], 'prices' : []},
        'RBs' : {'players' : [], 'projs' : [], 'prices' : []},
        'WRs' : {'players' : [], 'projs' : [], 'prices' : []},
        'TEs' : {'players' : [], 'projs' : [], 'prices' : []},
        'DSTs' : {'players' : [], 'projs' : [], 'prices' : []},
        'flexs' : {'players' : [], 'projs' : [], 'prices' : []}
        };
        //initialize plot
    setPlot(currentTeam)
function getTeamData(qbs, rbs, wrs, tes, dst, team, key) {
    var allPlayers = [qbs, rbs, wrs, tes, dst].flat(1);
    playerObjects = []
    
    team.forEach(name => {
        playerObjects.push(allPlayers.filter(row => row.Name == name)[0])
    })
    playerObjects.shift()
    if (key =='Price') {
        var price = playerObjects.map(function(row) {return row[key];})
                        .reduce((acc, val) => acc + val)
        return price
    } else if (key == 'Projection') {
        var projection = playerObjects.map(function(row) {return row[key];})
                                .reduce((acc, val) => acc + val)
        return projection
    };
}    

    teamLists = teams.map(elem => {
        var nameList = Object.values(elem).flat(1);
        price = getTeamData(qbs, rbs, wrs, tes, dst, nameList, 'Price'),
        projection =  getTeamData(qbs, rbs, wrs, tes, dst, nameList, 'Projection'),
        teamName =nameList.shift()
        nameList.unshift(price)
        nameList.unshift(projection)
        nameList.unshift(teamName)
        return nameList
    }) 
    console.log(teamLists)
    var table = d3.select('#tableBody')
    var trow = table.selectAll('tr')
        .data(teamLists).enter()
        .append('tr');
    var td = trow.selectAll("td")
        .data(function(d) {return d; })
        .enter()
        .append("td")
        .text(function(d) {return d;});
        
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
            currentTeam.QBs.players.push(this.value)
            var proj = d3.select(this).attr('proj')
            var price = d3.select(this).attr('price')
            currentTeam.QBs.projs.push(proj)
            currentTeam.QBs.prices.push(price)
            var list = d3.select('#qbList')
            addPlayerTag(list, currentTeam.QBs.players)
            counts['qbCount']++;
            updateRemoveButtonFunction(counts, currentTeam)
            setPlot(currentTeam)
            
    }
})
    d3.selectAll('.rbOpt').on('click', function() {
        if (counts['rbCount'] < 2) {
            currentTeam.RBs.players.push(this.value)
            var proj = d3.select(this).attr('proj')
            var price = d3.select(this).attr('price')
            currentTeam.RBs.projs.push(proj)
            currentTeam.RBs.prices.push(price)
            var list = d3.select('#rbList')
            addPlayerTag(list, currentTeam.RBs.players);
            counts['rbCount']++;
            updateRemoveButtonFunction(counts, currentTeam)
            setPlot(currentTeam)
            
    }
    })
    d3.selectAll('.wrOpt').on('click', function() {
        if (counts['wrCount'] < 3) {
            currentTeam.WRs.players.push(this.value)
            var proj = d3.select(this).attr('proj')
            var price = d3.select(this).attr('price')
            currentTeam.WRs.projs.push(proj)
            currentTeam.WRs.prices.push(price)
            var list = d3.select('#wrList')
            addPlayerTag(list, currentTeam.WRs.players);
            counts['wrCount']++;
            updateRemoveButtonFunction(counts, currentTeam)
            setPlot(currentTeam)
    }
    })
    d3.selectAll('.teOpt').on('click', function() {
        if (counts['teCount'] < 1) {
            currentTeam.TEs.players.push(this.value)
            var proj = d3.select(this).attr('proj')
            var price = d3.select(this).attr('price')
            currentTeam.TEs.projs.push(proj)
            currentTeam.TEs.prices.push(price)
            var list = d3.select('#teList')
            addPlayerTag(list, currentTeam.TEs.players);
            counts['teCount']++;
            updateRemoveButtonFunction(counts, currentTeam)
            setPlot(currentTeam)
            
    }
    })
    d3.selectAll('.dstOpt').on('click', function() {
        if (counts['dstCount'] < 1) {
            currentTeam.DSTs.players.push(this.value)
            var proj = d3.select(this).attr('proj')
            var price = d3.select(this).attr('price')
            currentTeam.DSTs.projs.push(proj)
            currentTeam.DSTs.prices.push(price)
            var list = d3.select('#dstList')
            addPlayerTag(list, currentTeam.DSTs.players);
            counts['dstCount']++;
            updateRemoveButtonFunction(counts, currentTeam)
            setPlot(currentTeam)
    }
    })
    d3.selectAll('.flexPositionOpt').on('click', function() {
        if (this.value == 'RB') {
            assignOptions(rbs, 'flexPlayer')
            updateFlexOptions(counts, currentTeam)
        } else if (this.value == 'WR') {
            assignOptions(wrs, 'flexPlayer')
            updateFlexOptions(counts, currentTeam)
        } else if (this.value == 'TE') {
            assignOptions(tes, 'flexPlayer')
            updateFlexOptions(counts, currentTeam)
        };
    })
    // d3.select("#teamNameSetter").html(this.value);
    d3.select('#nameSetter').on('change', function() {
        d3.select('#nameSetterButton').on('click', function() {
            var input = d3.select(this.parentNode.parentNode).select('#nameSetter')
            currentTeam.teamName = input.node().value
    });
    })
    
   d3.select('#submitButton').on('click', function () {
       // // // add team name secure meaning make sure 
       // // // team name is in place before this request is sent
        var teamPlayers = Object.values(currentTeam).map(position => position.players).flat(1)
        teamPlayers.shift()
        var teamList = teamPlayers.unshift(currentTeam.teamName)

        teamPlayers = teamPlayers.map(elem => { return elem.split(' ').join('-')})

        console.log(teamPlayers)
        if (teamList == 10) {
            urlString = `/${teamPlayers.join('/')}`
            console.log(urlString)
            window.location.replace(urlString)

        }
        
    })
    
});