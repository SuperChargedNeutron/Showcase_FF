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
    currentTeam = { 'teamName' : '',
        'QBs' : {'players' : [], 'projs' : [], 'prices' : []},
        'RBs' : {'players' : [], 'projs' : [], 'prices' : []},
        'WRs' : {'players' : [], 'projs' : [], 'prices' : []},
        'TEs' : {'players' : [], 'projs' : [], 'prices' : []},
        'DSTs' : {'players' : [], 'projs' : [], 'prices' : []},
        'flexs' : {'players' : [], 'projs' : [], 'prices' : []}
        };
    //initialize plot


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
var teamsProjData = teamLists.map(row => row[1]),
teamsPriceData = teamLists.map(row => row[2]);

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
    svgWidth = 650,
    svgHeight = 320,
    chartWidth = svgWidth - margin.left - margin.right,
    chartHeight = svgHeight - margin.top - margin.bottom;

    const svg = d3.select('#stackApp').append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)

    let chartGroup = svg.append("g")
        .attr("transform",  `translate(${margin.left}, ${margin.top})`)
    
        var xCurrentSelection = 'Price',
        yCurrentSelection = 'Projection',
        dataCurrentSelection = 'teamsStacked';

    let xLinearScale = xScale(teamsProjData, xCurrentSelection, chartWidth),
    yLinearScale = yScale(teamsPriceData, yCurrentSelection, chartHeight);

    let bottomAxis = d3.axisBottom(xLinearScale),
        leftAxis = d3.axisLeft(yLinearScale)

    

    let xAxis = chartGroup.append('g')
        .classed('x-axis', true)
        .attr('transform', `translate(0, ${chartHeight})`)
        .call(bottomAxis)

    let yAxis = chartGroup.append('g')
        .classed('y-axis', true)
        .classed('transform', `translate(${chartWidth}, 0)`)
        .call (leftAxis)
        let circlesGroup = chartGroup.append('g')
        .selectAll("dot") //change to circle?
        .data(playerData)
        .enter()
            .append('circle')
            .attr('cx', d => xLinearScale(parseFloat(d[xCurrentSelection])))
            .attr('cy', d => yLinearScale(parseFloat(d[yCurrentSelection])))
            .attr('r', d => d.income / 5000)
            .style('fill', 'gray')
            .style('opacity', .3)
            .attr('stroke', 'black')
            .attr('stroke-width', 2)
     

let circleLabelGroup = chartGroup.append('g')
        .selectAll("text")
        .data(data.names)
        .enter()
        .append("text")
        .attr('font-size', 12)
        .attr("font-fmaily", "Saira")
        .attr('stroke-width', 1)
        .text((d) => d.abbr)
        .attr("x", d => xLinearScale(parseFloat(d[xCurrentSelection])) - 6 )
        .attr("y", d => yLinearScale(parseFloat(d[yCurrentSelection])) + 4 )
        .attr('fill', 'white')

    let xlabelsGroup = chartGroup
        .append("g")
        .attr("transform", `translate(${chartWidth / 2}, ${chartHeight + 20})`)
    
    xlabelsGroup.append('text')
        .attr('x', 0)
        .attr('y', 20)
        .attr('value', 'poverty')
        .classed('active', true)
        .text('DraftKingz Projection')


    xlabelsGroup.selectAll('text').on('click', function() {
            let xLabel = d3.select(this)
            let xActiveLabel = xlabelsGroup.select('.active')
            let xValue = xLabel.attr('value')
            console.log(xValue)
            if (xValue != xCurrentSelection) {
                xLabel.classed('active', true)
                xActiveLabel.classed('active', false)
                xCurrentSelection = xValue
                xLinearScale = xScale(teamsProjData, xCurrentSelection, chartWidth)
                xAxis = renderXAxis(xLinearScale, xAxis)
                circlesGroup = renderCircles(
                    circlesGroup,
                    xLinearScale,
                    xCurrentSelection
                )
                circleLabelGroup = renderLabels(
                    circleLabelGroup,
                    xLinearScale,
                    xCurrentSelection
                )
            }
        })

    let ylabelsGroup = chartGroup
        .append("g")
        .attr("transform", `translate( ${(chartHeight / 2) }, ${0 - margin.left})`)
        .attr('transform', 'rotate(-90)')
    
ylabelsGroup.append('text')
        .attr('x', - (chartHeight / 2) - 20)
        .attr('y', - margin.left + 55 )
        .attr('value', 'aFPA')
        .classed('active', true)
        .text('aFPA')

ylabelsGroup.append('text')
        .attr('x', - (chartHeight / 2) - 20)
        .attr('y', - margin.left + 35)
        .attr('value', 'Projection')
        .classed('active', false)
        .text('Projection')




    // ylabelsGroup.selectAll('text').on('click', function() {
    //         let label = d3.select(this)
    //         let activeLabel = ylabelsGroup.select('.active')
    //         let value = label.attr('value')
    //         if (value != yCurrentSelection) {
    //             activeLabel.classed('active', false)
    //             label.classed('active', true)
    //             yCurrentSelection = value
    //             yLinearScale = yScale(data, yCurrentSelection)
    //             yAxis = renderYAxis(yLinearScale, yAxis)
    //             circlesGroup = renderYCircles(
    //                 circlesGroup,
    //                 yLinearScale,
    //                 yCurrentSelection
    //             )
    //             circleLabelGroup = renderYLabels(
    //                 circleLabelGroup,
    //                 yLinearScale,
    //                 yCurrentSelection
    //             )
    //         }
    // })
   
    var current = d3.select('#currentSelection')
                        .selectAll('ul')
                        .data(positions).enter()
                        .append('div')
                        .append('ul')
                        .classed('list-group', true)
                        .classed('positionList', true)
                        .attr('id', function(d) { return `${d}List`; })

    d3.selectAll('.qbOpt').on('click', function() {
        console.log(this.value)
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
       var teamName = currentTeam.teamName;
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
            console.log(urlString)
            window.location.replace(urlString)

        
        
    })
    
});