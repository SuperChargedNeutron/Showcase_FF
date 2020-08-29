d3.json('/stack_app_data').then(function(data){
    var playerData = data['names'],
    teams = data['teams'];
    var positions = ['qb', 'rb', 'wr', 'te', 'dst', 'flex'],
    qbs = playerData.filter(row => row.Pos === 'QB'),
    rbs = playerData.filter(row => row.Pos === 'RB'),
    wrs = playerData.filter(row => row.Pos === 'WR'),
    tes = playerData.filter(row => row.Pos === 'TE'),
    dst = playerData.filter(row => row.Pos === 'DST');

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
    currentTeam = { 'teamName' : [],
        'QBs' : {'players' : [], 'projs' : [], 'prices' : []},
        'RBs' : {'players' : [], 'projs' : [], 'prices' : []},
        'WRs' : {'players' : [], 'projs' : [], 'prices' : []},
        'TEs' : {'players' : [], 'projs' : [], 'prices' : []},
        'DSTs' : {'players' : [], 'projs' : [], 'prices' : []},
        'flexs' : {'players' : [], 'projs' : [], 'prices' : []}
        };


var teamLists = teams.map(elem => {
    var nameList = Object.values(elem).flat(1);
    price = getTeamData(playerData, nameList, 'DK_Price'),
    projection =  getTeamData(playerData, nameList, 'DK_Proj'),
    teamName = nameList.shift();
    nameList.unshift(Math.round(price / projection*100)/100)
    nameList.unshift(Math.round(price*100)/100)
    nameList.unshift(Math.round(projection*100)/100)
    nameList.unshift(teamName)
    return nameList
});
var teamsData = teamLists.map(row => [row[0], row[2], row[1]])
var table = d3.select('#tableBody')
var trow = table.selectAll('tr')
    .data(teamLists).enter()
    .append('tr');
var td = trow.selectAll("td")
    .data(function(d) {return d; })
    .enter()
    .append("td")
    .text(function(d) {return d;});
    
    // Initial Chart plotting
    const margin = { top: 50, right: 50, bottom: 70, left: 80 },
    svgWidth = 660,
    svgHeight = 470,
    chartWidth = svgWidth - margin.left - margin.right,
    chartHeight = svgHeight - margin.top - margin.bottom;

    const svg = d3.select('#stackApp').append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)

    let chartGroup = svg.append("g")
        .attr('id', 'chartGroup')
        .attr("transform",  `translate(${margin.left}, ${margin.top})`)
    
        var yCurrentSelection = 'Projection',
        dataCurrentSelection = 'teamStacked',
        xCurrentSelection = 'Price';

    let xLinearScale = xScale(teamsData.map(row => {return row[1]}), chartWidth),
    yLinearScale = yScale(teamsData.map(row => {return row[2]}), chartHeight);

    let bottomAxis = d3.axisBottom(xLinearScale),
        leftAxis = d3.axisLeft(yLinearScale)

    let xAxis = chartGroup.append('g')
        .classed('x-axis', true)
        .attr('transform', `translate(0, ${chartHeight})`)
        .call(bottomAxis)

    let yAxis = chartGroup.append('g')
        .classed('y-axis', true)
        .classed('transform', `translate(${chartWidth}, 0)`)
        .call(leftAxis)

    circleColors = ['#B31217', '#B35F12', '#B8A211', '#12B816', '#1450B5', '#1FA5B8', '#ADB87D', '#B87DB7', '#AABDB1', '#99A7BD']

    var teamCircleColor = d3.scaleOrdinal()
        .domain(teamsData.map(row => {return row[0]}))
        .range(circleColors);

    var tooltip = d3.select("#stackApp")
        .append("div")
        .classed('tooltip', true)
        .style("visibility", "hidden");

    let circlesGroup = chartGroup.append('g').attr('id', 'circleGroup')
    circlesGroup.selectAll("circle") //change to circle?
        .data(teamsData).enter()
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
     
    let xlabelsGroup = chartGroup
        .append("g")
        .attr("transform", `translate(${chartWidth / 2}, ${chartHeight + 20})`)
    xlabelsGroup.append('text')
        .attr('x', 0)
        .attr('y', 20)
        .attr('value', 'Price')
        .classed('active', true)
        .text('Price')

    let ylabelsGroup = chartGroup
        .append("g")
        .attr("transform", `translate( ${(chartHeight / 2) }, ${0 - margin.left})`)
        .attr('transform', 'rotate(-90)')

ylabelsGroup.append('text')
        .attr('x', - (chartHeight / 2) )
        .attr('y', - margin.left + 20)
        .attr('value', 'aFPA')
        .classed('active', false)
        .text('aFPA')

ylabelsGroup.append('text')
        .attr('x', - (chartHeight / 2) - 40)
        .attr('y', - margin.left + 45 )
        .attr('value', 'Projection')
        .classed('active', true)
        .text('Projection (Avg)')


    let dataLabelsGroup = chartGroup
        .append("g")
        .attr("transform", `translate( ${0 + margin.top}, ${.5 * svgWidth})`)

    dataLabelsGroup.append('text')
        .attr('x',  (-25) )
        .attr('y', -340)
        .attr('value', 'teamBuild')
        .classed('active', false)
        .text('Team Builder')
    dataLabelsGroup.append('text')
        .attr('x',  135) 
        .attr('y', -340)
        .attr('value', 'teamPlayers')
        .classed('active', false)
        .text('Teams: Players')
    dataLabelsGroup.append('text')
        .attr('x', 295) 
        .attr('y', -340)
        .attr('value', 'teamStacked')
        .classed('active', true)
        .text('Teams: Stacked')

    dataLabelsGroup.selectAll('text').on('click', function() {
            let tag = d3.select(this),
            activeLabel = dataLabelsGroup.select('.active'),
            tagValue = tag.attr('value')
            if (tagValue != dataCurrentSelection) {
                newTag = tag.classed('active', true)
                activeLabel.classed('active', false)
                dataCurrentSelection = newTag.attr('value')

                if (dataCurrentSelection == 'teamStacked'){
                    xLinearScale = xScale(
                        teamsData.map(row => {return row[1]}), 
                        chartWidth
                        )
                    yLinearScale = yScale(
                        teamsData.map(row => {return row[2]}),
                         chartHeight
                        )
                    xAxis = renderXAxis(xLinearScale, xAxis)
                    yAxis = renderYAxis(yLinearScale, yAxis)
                    circlesGroup = renderCircles(
                        xLinearScale,
                        yLinearScale, 
                        yCurrentSelection,
                        teamsData,
                        dataCurrentSelection,
                        tooltip
                    )

                } else if (dataCurrentSelection == 'teamPlayers') {
                    
                    allTeamPlayers = teams.map(elem => {
                        var nameList = Object.values(elem).flat(1);
                        teamPlayers = getTeamData(playerData, nameList, 'players')
                        return teamPlayers                        
                }).flat(1)
                xLinearScale = xScale(
                    allTeamPlayers.map(obj => obj['DK_Price']), 
                    chartWidth
                    )
                yLinearScale = yScale(
                    [allTeamPlayers.map(obj => obj['DK_Flr']), 
                        allTeamPlayers.map(obj => obj['DK_Proj']),
                        allTeamPlayers.map(obj => obj['DK_Ceil'])].flat(1),
                     chartHeight
                    )
                xAxis = renderXAxis(xLinearScale, xAxis)
                yAxis = renderYAxis(yLinearScale, yAxis)
                circlesGroup = renderCircles(
                    xLinearScale,
                    yLinearScale, 
                    yCurrentSelection,
                    allTeamPlayers,
                    dataCurrentSelection, 
                    tooltip
                )
            } else if (dataCurrentSelection == 'teamBuild') {
                plotCurrentTeam(currentTeam, 
                    chartWidth, chartHeight, 
                    xAxis, yAxis, 
                    dataCurrentSelection, yCurrentSelection,
                    tooltip)
            }}
        })
    
    ylabelsGroup.selectAll('text').on('click', function() {
            let clickedLabel = d3.select(this).attr('value')
            let activeLabel = ylabelsGroup.select('.active').attr('value')
            // if (value != yCurrentSelection) {
            //     activeLabel.classed('active', false)
            //     label.classed('active', true)
            //     yCurrentSelection = value
            //     yLinearScale = yScale(data, yCurrentSelection)
            //     yAxis = renderYAxis(yLinearScale, yAxis)
            //     circlesGroup = renderYCircles(
            //         circlesGroup,
            //         yLinearScale,
            //         yCurrentSelection
            //     )
            //     circleLabelGroup = renderYLabels(
            //         circleLabelGroup,
            //         yLinearScale,
            //         yCurrentSelection
            //     )
            // }
    })
   
    var current = d3.select('#currentTeam')
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
            updateRemoveButtonFunction(counts, currentTeam, chartWidth, chartHeight, xAxis, yAxis, dataCurrentSelection, yCurrentSelection)
            if (dataCurrentSelection == 'teamBuild') {
                plotCurrentTeam(currentTeam, 
                    chartWidth, chartHeight, 
                    xAxis, yAxis, 
                    dataCurrentSelection, yCurrentSelection,
                    tooltip)
            }
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
            updateRemoveButtonFunction(counts, currentTeam, chartWidth, chartHeight, xAxis, yAxis, dataCurrentSelection, yCurrentSelection)
            if (dataCurrentSelection == 'teamBuild') {
                plotCurrentTeam(currentTeam, 
                    chartWidth, chartHeight, 
                    xAxis, yAxis, 
                    dataCurrentSelection, yCurrentSelection,
                    tooltip)
            }

            
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
            updateRemoveButtonFunction(counts, currentTeam, chartWidth, chartHeight, xAxis, yAxis, dataCurrentSelection, yCurrentSelection)
            if (dataCurrentSelection == 'teamBuild') {
                plotCurrentTeam(currentTeam, 
                    chartWidth, chartHeight, 
                    xAxis, yAxis, 
                    dataCurrentSelection, yCurrentSelection,
                    tooltip)
            }
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
            updateRemoveButtonFunction(counts, currentTeam, chartWidth, chartHeight, xAxis, yAxis, dataCurrentSelection, yCurrentSelection)
            if (dataCurrentSelection == 'teamBuild') {
                plotCurrentTeam(currentTeam, 
                    chartWidth, chartHeight, 
                    xAxis, yAxis, 
                    dataCurrentSelection, yCurrentSelection,
                    tooltip)
            }
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
            updateRemoveButtonFunction(counts, currentTeam, chartWidth, chartHeight, xAxis, yAxis, dataCurrentSelection, yCurrentSelection)
            if (dataCurrentSelection == 'teamBuild') {
                plotCurrentTeam(currentTeam, 
                    chartWidth, chartHeight, 
                    xAxis, yAxis, 
                    dataCurrentSelection, yCurrentSelection,
                    tooltip)
            }
    }
    })
    d3.selectAll('.flexPositionOpt').on('click', function() {
        if (this.value == 'RB') {
            assignOptions(rbs, 'flexPlayer')
             updateFlexOptions(counts, currentTeam, chartWidth, chartHeight, xAxis, yAxis, dataCurrentSelection, yCurrentSelection, tooltip)
        } else if (this.value == 'WR') {
            assignOptions(wrs, 'flexPlayer')
             updateFlexOptions(counts, currentTeam, chartWidth, chartHeight, xAxis, yAxis, dataCurrentSelection, yCurrentSelection, tooltip)
        } else if (this.value == 'TE') {
            assignOptions(tes, 'flexPlayer')
             updateFlexOptions(counts, currentTeam, chartWidth, chartHeight, xAxis, yAxis, dataCurrentSelection, yCurrentSelection, tooltip)
        };
    })

        d3.select('#nameSetterButton').on('click', function() {
            var input = d3.select(this.parentNode.parentNode).select('#nameSetter')
            while (currentTeam.teamName.length) {
                currentTeam.teamName.pop();
              }
            currentTeam.teamName.push(input.node().value)
    });
    
   d3.select('#submitButton').on('click', function () {
        if ( currentTeam.teamName[0] == undefined || currentTeam.teamName[0] == "") {
           teamName = 'default'
       } else if (currentTeam.teamName[0] != undefined && currentTeam.teamName[0] != "") {
            teamName = currentTeam.teamName[0];
       };
       if (currentTeam.QBs.players[0] != undefined) { 
           qb = currentTeam.QBs.players[0]
        } else if  (currentTeam.QBs.players[0] == undefined) {
            qb = 'nan'
        };
        if (currentTeam.RBs.players[0] != undefined) { 
            rb1 = currentTeam.RBs.players[0] 
         } else if  (currentTeam.RBs.players[0] == undefined) {
             rb1 = 'nan'
         };
         if (currentTeam.RBs.players[1] != undefined) { 
            rb2 = currentTeam.RBs.players[1] 
         } else if  (currentTeam.RBs.players[1] == undefined) {
             rb2 = 'nan'
         };
         if (currentTeam.WRs.players[0] != undefined) { 
            wr1 = currentTeam.WRs.players[0] 
         } else if  (currentTeam.WRs.players[0] == undefined) {
             wr1 = 'nan'
         };
         if (currentTeam.WRs.players[1] != undefined) { 
            wr2 = currentTeam.WRs.players[1] 
         } else if  (currentTeam.WRs.players[1] == undefined) {
             wr2 = 'nan'
         };
         if (currentTeam.WRs.players[2] != undefined) { 
            wr3 = currentTeam.WRs.players[2] 
         } else if  (currentTeam.WRs.players[2] == undefined) {
             wr3 = 'nan'
         };
         if (currentTeam.TEs.players[0] != undefined) { 
            te = currentTeam.TEs.players[0] 
         } else if  (currentTeam.TEs.players[0] == undefined) {
             te = 'nan'
         };
         if (currentTeam.DSTs.players[0] != undefined) { 
            dst = currentTeam.DSTs.players[0] 
         } else if  (currentTeam.DSTs.players[0] == undefined) {
             dst = 'nan'
         };
         if (currentTeam.flexs.players[0] != undefined) { 
            flex = currentTeam.flexs.players[0] 
         } else if  (currentTeam.flexs.players[0] == undefined) {
             flex = 'nan'
         };


        var teamPlayers = [teamName, qb, rb1, rb2, wr1, wr2, wr3, te, dst, flex]
        teamPlayers = teamPlayers.map(elem => { return elem.split(' ').join('-')})
        urlString = `/${teamPlayers.join('/')}`
        window.location.replace(urlString)
    })
    
});