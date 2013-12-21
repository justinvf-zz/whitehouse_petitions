var w = 1000,
    h = 500,
    margin = 40;
var dataPath = "sequestration.json";

d3.json(dataPath, ready);

function getDates(ar) {
    ar.forEach(function(d) {
	d.date = new Date(d.date);
    });
    return ar.map(function(d) { return d.date });
}

var activeItem;

function updateArticle(article) {
    if (activeItem) {
	activeItem.active = false;
    }
    article.active = true;
    activeItem = article;

    d3.select('#article_url')
	.text(article['title'])
	.attr('href', article['link']);

    d3.select("#article_text")
	.text(article['teaser']);
}

function updatePetition(data) {
    d3.select('#petition_text')
	.text(data['petition_text']);

    d3.select('#petition_url')
	.attr('href', data['petition_url'])
	.text(data['petition_title']);
}



function getWeekStart(d, dayOfWeek) {
    // Get the given day of the week in d's week.
    // BS function but I really don't want a whole js library
    var toReturn = new Date(d);
    if (toReturn.getDay() > 0) {
	toReturn.setDate(d.getDate() - d.getDay() + dayOfWeek);
    }
    toReturn.setHours(0);
    toReturn.setMinutes(0);
    toReturn.setSeconds(0);
    return toReturn;
}

function ready(error, data) {
    allDates = getDates(data['articles']).concat(getDates(data['signature_counts']));
    articles = data['articles']

    var activeArticle = 0;

    updateArticle(data['articles'][activeArticle]);
    updatePetition(data);

    if (data['petition_close']) {
	allDates.push(new Date(data['petition_close']));
    }
    
    var cirlesPerWeek = {};

    var dateRange = d3.extent(allDates);

    var activeBar;

    var weeklyCounts = d3.map();
    for (var i = 0; i < articles.length; i++) {
	startOfWeek = getWeekStart(articles[i].date, 0);
	if (weeklyCounts.has(startOfWeek)) {
	    articles[i]['week_index'] = weeklyCounts.get(startOfWeek) + 1;
	} else {
	    articles[i]['week_index'] = 0;
	}
	weeklyCounts.set(startOfWeek, articles[i]['week_index'])
    }

    x = d3.time.scale()
	.domain(dateRange)
	.rangeRound([margin/2, w - margin/2]);

    xAxis = d3.svg.axis()
	.scale(x)
	.orient('top')
	.tickFormat(d3.time.format('%m/%d/%y'))
	.tickSize(10)
	.ticks(6)
	.tickPadding(10);

    var maxSigs = d3.max(data['signature_counts'],
			 function(d) { return d['count']; });

    yTop = d3.scale.linear()
	.domain([0, maxSigs])
	.rangeRound([h/2, margin]);

    yTopAxis = d3.svg.axis().scale(yTop).orient("right");

    yBottom = d3.scale.linear()
	.domain([0, d3.max(weeklyCounts.values()) + 1])
	.range([h/2,  h - margin]);

    svg = d3.select("#timeline").append("svg")
	.attr("width", w)
	.attr("height", h);

    svg.append('g')
	.attr('class', 'x axis')
	.attr('transform', 'translate(0, ' + margin + ')')
	.call(xAxis);

    svg.append("g").attr("class", "y axis").call(yTopAxis);


    svg.selectAll('rectangle').data(data['signature_counts']).enter()
	.append('rect')
	.attr('x', function(d) {return x(d.date)})
	.attr('y', function(d) {return yTop(d.count)})
	.attr('width', 4)
	.attr('height', function(d) {return h/2 - yTop(d.count)})
	.append("svg:title")
	.text(function(d) { return d.date.getMonth() + '/' + d.date.getDate() + ': ' + d.count });

    svg.selectAll('circle').data(data['articles']).enter()
	.append('circle')
	.attr('cx', function(d) {return x(getWeekStart(d.date, 3)); })
	.attr('cy', function(d) {return yBottom(d.week_index) + margin/3; })
	.attr('r', 12)
	.on('mouseover', function(d) {
	    updateArticle(d);
	    d3.selectAll('circle').classed('active', function(d) {return d.active;});
	});
}
