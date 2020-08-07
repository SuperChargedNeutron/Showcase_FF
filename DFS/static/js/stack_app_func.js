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
                return d.Player;
            }})
        .classed(`${position}Opt`, true)
        .attr('proj', function (d) {return d.DK_Proj})
        .attr('price', function (d) {return d.DK_Price})
        .text(function(d) { 
            if (position == 'flexPosition') {
                return d; 
            } else if (position != 'flexPosition') {
                return d.Player;
            }})
}


function xScale (data, xCurrentSelection, chartWidth) {
    let xMax = d3.max(data.map(d => parseFloat(d))),
        xMin = d3.min(data.map(d => parseFloat(d)))

    let xLinearScale = d3.scaleLinear()
        .domain([xMin - 1, xMax ])
        .range([0, chartWidth])

    return xLinearScale 
}
function yScale ( data, yCurrentSelection, chartHeight) {
    let yMin = d3.min(data.map(d => parseFloat(d))),
        yMax = d3.max(data.map(d => parseFloat(d)))

    let yLinearScale = d3.scaleLinear()
        .domain([yMin - 1, yMax])
        .range([chartHeight, 0])

    return yLinearScale 
}

function renderXAxis (newXScale, xAxis) {
    let bottomAxis = d3.axisBottom(newXScale)
    
    xAxis
    .transition()
    .duration(1000)
    .call(bottomAxis)

    return xAxis
}

function renderYAxis (newYScale, yAxis) {
    let leftAxis = d3.axisLeft(newYScale)
    yAxis
    .transition()
    .duration(1000)
    .call(leftAxis)

    return yAxis
}

function renderCircles(circlesGroup, newXScale, xCurrentSelection) {
    circlesGroup
        .transition()
        .duration(1000)
        .attr('cx', d => newXScale(parseFloat(d[xCurrentSelection])))
    
    return circlesGroup
}
function renderYCircles(circlesGroup, newYScale, yCurrentSelection) {
    circlesGroup
        .transition()
        .duration(1000)
        .attr('cy', d => newYScale(parseFloat(d[yCurrentSelection])))
    
    return circlesGroup
}
function getTeamData(playerData, team, key) {
    var playerObjects = [];
    
    team.forEach(name => {
        playerObjects.push(playerData.filter(row => {return row.Player == name })[0])
    })

    playerObjects.shift()
    console.log(playerData)
    console.log(playerObjects)
    if (key =='DK_Price') {
        var price = playerObjects.map(row => row[key])
                        .reduce((acc, val) => acc + val)
        return price
    } else if (key == 'DK_Proj') {
        var projection = playerObjects.map(row => row[key])
                                .reduce((acc, val) => acc + val)
        return projection
    };
}   