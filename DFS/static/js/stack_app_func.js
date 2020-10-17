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

function updateRemoveButtonFunction(counts, currentTeam, chartWidth, chartHeight, xAxis, yAxis, dataCurrentSelection, yCurrentSelection) {
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
            } else if (this.parentNode.parentNode.id == 'rbList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam.RBs.players.indexOf(playerText)
                currentTeam.RBs.players.pop(playerIndex)
                currentTeam.RBs.prices.pop(playerIndex)
                currentTeam.RBs.projs.pop(playerIndex)
                player.remove()
                counts['rbCount']--;
            } else if (this.parentNode.parentNode.id == 'wrList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam.WRs.players.indexOf(playerText)
                currentTeam.WRs.players.pop(playerIndex)
                currentTeam.WRs.prices.pop(playerIndex)
                currentTeam.WRs.projs.pop(playerIndex)
                player.remove()
                counts['wrCount']--;
            } else if (this.parentNode.parentNode.id == 'teList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam.TEs.players.indexOf(playerText)
                currentTeam.TEs.players.pop(playerIndex)
                currentTeam.TEs.prices.pop(playerIndex)
                currentTeam.TEs.projs.pop(playerIndex)
                player.remove()
                counts['teCount']--;
            } else if (this.parentNode.parentNode.id == 'dstList') {
                player = d3.select(this.parentNode)
                playerText = player.text()
                playerIndex = currentTeam.DSTs.players.indexOf(playerText)
                currentTeam.DSTs.players.pop(playerIndex)
                currentTeam.DSTs.prices.pop(playerIndex)
                currentTeam.DSTs.projs.pop(playerIndex)
                player.remove()
                counts['dstCount']--;
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
            plotCurrentTeam(currentTeam, chartWidth, chartHeight, xAxis, yAxis, dataCurrentSelection, yCurrentSelection)
        })
}

function plotCurrentTeam(currentTeam, chartWidth, chartHeight, xAxis, yAxis, dataCurrentSelection, yCurrentSelection, tooltip) {
    dataExtracted = extractCurrentTeamData(currentTeam)
    xLinearScale = xScale(
        dataExtracted.map(row => row[1]), 
        chartWidth
        )
        yLinearScale = yScale(
            dataExtracted.map( row => row[2]),
                chartHeight
            )
        xAxis = renderXAxis(xLinearScale, xAxis)
        yAxis = renderYAxis(yLinearScale, yAxis)
        circlesGroup = renderCircles(
            xLinearScale,
            yLinearScale, 
            yCurrentSelection,
            dataExtracted,
            dataCurrentSelection, 
            tooltip
        )
}

function updateFlexOptions(counts, currentTeam, chartWidth, chartHeight, xAxis, yAxis, dataCurrentSelection, yCurrentSelection, tooltip) {
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
            if (dataCurrentSelection == 'teamBuild') {
                plotCurrentTeam(currentTeam, chartWidth, chartHeight, xAxis, yAxis, dataCurrentSelection, yCurrentSelection, tooltip)
            }
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
                return d.player;
            }})
        .classed(`${position}Opt`, true)
        .attr('proj', function (d) {return d.C_Proj})
        .attr('price', function (d) {return d.salary})
        .text(function(d) { 
            if (position == 'flexPosition') {
                return d; 
            } else if (position != 'flexPosition') {
                return d.player;
            }})
}


function xScale (data, chartWidth) {
    let xMax = d3.max(data.map(d => parseFloat(d))),
        xMin = d3.min(data.map(d => parseFloat(d)))

    let xLinearScale = d3.scaleLinear()
        .domain([xMin - 1000, xMax  + 1000])
        .range([0, chartWidth])

    return xLinearScale 
}

function yScale ( data, chartHeight) {
    let yMin = d3.min(data.map(d => parseFloat(d))),
        yMax = d3.max(data.map(d => parseFloat(d)))

    let yLinearScale = d3.scaleLinear()
        .domain([yMin - 5, yMax + 5])
        .range([chartHeight, 0])

    return yLinearScale 
}

function renderXAxis (newXScale, xAxis) {
    let bottomAxis = d3.axisBottom(newXScale)
    
    xAxis
    .call(bottomAxis)

    return xAxis
}

function renderYAxis (newYScale, yAxis) {
    let leftAxis = d3.axisLeft(newYScale)
    yAxis
    .call(leftAxis)

    return yAxis
}

function extractCurrentTeamData (currentTeam) {
    dataExtracted = []
                Object.keys(currentTeam).forEach(key => {
                if (key =='teamName') {
                    return undefined
                }
                for (i=0; i < currentTeam[key]['players'].length; i++) {
                    dataExtracted.push([currentTeam[key]['players'][i], currentTeam[key]['prices'][i], currentTeam[key]['projs'][i]])
                }
                }
            )
    return dataExtracted
}
function renderCircles(xLinearScale, yLinearScale, yCurrentSelection, data, dataCurrentSelection, tooltip) {

    circleGroup = d3.select('#circleGroup');
    circleGroup.selectAll('circle').remove().exit();
    circleGroup.selectAll('line.error').remove().exit();
    if (dataCurrentSelection == 'teamStacked') {

        circleColors = ['#9B5DE5', '#f15bb5', '#fee440','#c1839f', '#00bbf9', '#00f5d4', '#ff5a5f', '#087e8b']
        var teamCircleColor = d3.scaleOrdinal()
            .domain(data.map(row => {return row[0]}))
            .range(circleColors);

        circleGroup.selectAll("circle") //change to circle?
        .data(data).enter()
                .append('circle')
                .attr('cx', d => xLinearScale(parseFloat(d[1])))
                .attr('cy', d => yLinearScale(parseFloat(d[2])))
                .attr('r', 5)
                .style('fill', d => teamCircleColor(d[0]))
                .style('opacity', .8)
                .attr('stroke', 'black')
                .attr('stroke-width', .5)
                .on("mouseover", function(d) {	
                    tooltip.transition()		
                        .duration(200)		
                        .style("opacity", .9)
                    tooltip.html(`${d[0]} <br/> ${d[2]}`)	
                        .style("left", (d3.event.pageX) + "px")		
                        .style("top", (d3.event.pageY - 28) + "px")
                        .style("visibility", "visible");	
                    })					
                .on("mouseout", function(){return tooltip.style("visibility", "hidden");});
        
    return circleGroup
    } else if ( dataCurrentSelection == 'teamPlayers') {
        circleColors = ['#9B5DE5', '#f15bb5', '#fee440','#c1839f', '#00bbf9', '#00f5d4', '#ff5a5f', '#087e8b']
        var teamCircleColor = d3.scaleOrdinal()
            .domain(data.map(row => {return row['teamName']}))
            .range(circleColors);

        circleGroup.selectAll("circle")
            .data(data).enter()
            .append('circle')
            .attr('cx', d => xLinearScale(parseFloat(d['salary'])))
            .attr('cy', d => yLinearScale(parseFloat(d['C_Proj'])))
            .attr('r', 5)
            .style('fill', (d, i) => teamCircleColor(d['teamName']))
            .style('opacity', .8)
            .attr('stroke', 'black')
            .attr('stroke-width', .5)
            .on("mouseover", function(d) {	
                tooltip.transition()		
                    .duration(200)		
                    .style("opacity", .9)
                tooltip.html(`${d['player']} <br/> ${d['teamName']}`)	
                    .style("left", (d3.event.pageX) + "px")		
                    .style("top", (d3.event.pageY - 28) + "px")
                    .style("visibility", "visible");	
                })					
            .on("mouseout", function(){return tooltip.style("visibility", "hidden");});

        var lines = circleGroup
            .selectAll('line')
            .data(data);
        lines.enter()
            .append('line')
            .attr('class', 'error')
            .attr('x1', function(d) { return xLinearScale(parseFloat(d['salary'])); })
            .attr('x2', function(d) { return xLinearScale(parseFloat(d['salary'])); })
            .attr('y1', function(d) { return yLinearScale(parseFloat(d['C_Ceil'])); })
            .attr('y2', function(d) { return yLinearScale(parseFloat(d['C_Floor'])); });
        return circleGroup
    } else if ( dataCurrentSelection == 'teamBuild') {
        circleGroup.selectAll("circle")
            .data(data).enter()
            .append('circle')
            .attr('cx', d => xLinearScale(parseFloat(d[1])))
            .attr('cy', d => yLinearScale(parseFloat(d[2])))
            .attr('r', 5)
            .style('fill', 'gray')
            .style('opacity', .8)
            .attr('stroke', 'black')
            .attr('stroke-width', .5)
            .on("mouseover", function(d) {	
                tooltip.transition()		
                    .duration(200)		
                    .style("opacity", .9)
                tooltip.html(`${d[0]} <br/> ${d[2]}`)	
                    .style("left", (d3.event.pageX) + "px")		
                    .style("top", (d3.event.pageY - 28) + "px")
                    .style("visibility", "visible");	
                })					
            .on("mouseout", function(){return tooltip.style("visibility", "hidden");});
    }
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
    teamName = team[0]
    team.forEach(name => {
        playerObjects.push(playerData.filter(row => {return row.player == name })[0])
    })

    playerObjects.shift()
    var playerObjects = playerObjects.filter(function (el) {
        return el != undefined;
      });

    if (key == 'salary') {
        var price = playerObjects.map(row => parseFloat(row[key]))
                        .reduce((acc, val) => acc + val)
        return price
    } else if (key == 'C_Proj') {
        var projection = playerObjects.map(row => parseFloat(row[key]))
                                .reduce((acc, val) => acc + val)
        return projection
    } else if (key == 'players') {
        let mappedObjects = playerObjects.map(obj =>{
            var outDict = {'teamName' : teamName}
            Object.entries(obj).forEach((key, val) => {
                outDict[key[0]] = key[1]
            });
            return outDict})

        return mappedObjects
    };
}   