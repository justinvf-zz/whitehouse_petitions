var w = 1000,
    h = 500,
    margin = 50;
var dataPath = "sequestration.json";

d3.json(dataPath, ready);

function getDates(ar) {
    ar.forEach(function(d) {
	d.date = new Date(d.date);
    });
    return ar.map(function(d) { return d.date });
}

function updateArticle(article) {
    d3.select('article_url')
	.text(article['title'])
	.attr('href', article['link']);
}


function ready(error, data) {
    allDates = getDates(data['articles']).concat(getDates(data['signature_counts']));

    updateArticle(data['articles'][1]);

    if (data['petition_close']) {
	allDates.push(new Date(data['petition_close']));
    }
    
    dateRange = d3.extent(allDates);

    console.log(dateRange);

    xScale = d3.time.scale().domain(dateRange).rangeRound([margin, w - margin]);

    var maxSigs = d3.max(data['signature_counts'],
			 function(d) { return d['count']; });

    yScale = d3.scale.linear()
	.domain([0, maxSigs])
	.rangeRound([h - margin, margin]);

    svg = d3.select("#timeline").append("svg")
	.attr("width", w)
	.attr("height", h);

    svg.selectAll('rectangle').data(data['signature_counts']).enter()
	.append('rect')
	.attr('x', function(d) {return xScale(d.date)})
	.attr('y', function(d) {return yScale(d.count)})
	.attr('width', 4)
	.attr('height', function(d) {return h - yScale(d.count)});

    svg.selectAll('circle').data(data['articles']).enter()
	.append('circle')
	.attr('cx', function(d) {return xScale(d.date); })
	.attr('cy', h / 2)
	.attr('r', 3);
}
