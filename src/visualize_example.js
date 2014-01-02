if (!window.location.hash) {
    window.location.hash = 0
}

var index = +(window.location.hash.substr(1))

var margin = {top: 40, right: 40, bottom: 40, left: 40},
    width = 900 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;
    
// Fraction that we break the svg's vertical layout into
var BREAKS = 8;

// Hard-coded.. Will change later.
var NUM_BLOBS = 61;

var x = d3.time.scale().rangeRound([0, width]);
var y = d3.scale.linear().rangeRound([6 * height / BREAKS, margin.top]);

function getBlobPath(i) {
    return "blobs/blob-" + i + ".json";
}

d3.json(getBlobPath(index), ready);

function switchContent(inc) {
    index += inc;
    index = index < 0 ? NUM_BLOBS - 1 : index % NUM_BLOBS;
    window.location.hash = index;
    d3.json(getBlobPath(index), ready);
}

d3.select('#leftNav').on('click', function() {
    switchContent(-1);
});

d3.select('#rightNav').on('click', function() {
    switchContent(1);
});

function addDates(ar) {
    ar.forEach(function(d) {
	d.date = new Date(d.date);
    });
}

function getDates(ar) {
    return ar.map(function(d) { return d.date });
}

function jiggle(x, range) {
    return Math.round(Math.random() * range - range/2 + x);
}

function ready(error, data) {
    d3.select('#chartContent').remove()

    var chartContent = d3.select('#chart').append('div').attr('id', 'chartContent');
    var petitionBody = chartContent.append('div').attr('id', 'petition_data');
    var timeline = chartContent.append('div').attr('id', 'timeline')
    var articles = chartContent.append('div').attr('id', 'articles')

    addDates(data.articles);
    addDates(data.signature_counts);

    data.articles.sort(function(a,b) { return a.date - b.date; })
    data.signature_counts.sort(function(a,b) { return a.date - b.date; })

    var allDates = getDates(data.articles).concat(getDates(data.signature_counts));

    var dateRange = d3.extent(allDates);

    x.domain([new Date('2013-01-01'), new Date('2014-01-01')]);

    var maxSigs = d3.max(data.signature_counts, function(d) { return d.count; });
    y.domain([0, maxSigs]);


    petitionBody
	.append('a')
	.attr('href', data.petition_url)
	.append('h1')
	.text(data.petition_title);

    petitionBody
	.append('p')
	.text(data.petition_text);

    var svg = timeline.append('svg')
	.attr('width', width + margin.left + margin.right)
	.attr('height', height + margin.top + margin.bottom)
	.append('g')
	.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    svg.selectAll('.signatureLine')
	.data(data.signature_counts)
	.enter()
	.append('line')
	.classed('signatureLine', true)
	.attr('x1', function(d) { return x(d.date); })
	.attr('y1', function(d) { return y(d.count); })
	.attr('x2', function(d) { return x(d.date); })
	.attr('y2', function(d) { return 6 * height / BREAKS; });

    svg.selectAll('.articleLine')
	.data(data.articles)
	.enter()
	.append('line')
	.classed('articleLine', true)
	.attr('x1', function(d) { return x(d.date)})
	.attr('x2', function(d) { return jiggle(x(d.date), 9)} )
	.attr('y1', 7 * height / BREAKS)
	.attr('y2', height);

    xAxis = d3.svg.axis()
	.scale(x)
	.orient('bottom')
	.tickFormat(d3.time.format('%B'))
	.ticks(6)
	.tickPadding(10);

    yAxis = d3.svg.axis().scale(y).orient('left');

    var dateFormatter = d3.time.format('%B %d');

    svg.append('g')
	.attr('class', 'y axis')
	.call(yAxis)
	.append('text')
	.text('Signatures per Day')
	.attr('transform', 'translate(0,' + margin.top + ')')
	.style('font-weight', 'bold');

    svg.append('g')
	.attr('class', 'x axis')
	.attr('transform', 'translate(0, ' + (6 * height / BREAKS) + ')')
	.call(xAxis);

    var numArticles = data.articles.length;

    var articleStart = data.articles[Math.round((data.articles.length) / 4)].date;
    var articleEnd = data.articles[Math.round((data.articles.length) / 2)].date;

    var brush = d3.svg.brush().x(x)
	.on('brush', brushmove)
	.on('brushend', brushend)
	.extent([articleStart, articleEnd]);

    svg.append('g')
	.attr('class', 'brush')
	.call(brush)
	.selectAll('rect')
	.attr('height', height);

    svg.append('text')
	.text('Related Articles')
	.attr('transform', 'translate(0,' + (margin.top + 6 * height / BREAKS) + ')')
	.style('font-weight', 'bold');


    function inBound(d, s) {
	return s[0] <= d.date && d.date <= s[1];
    }

    function brushmove() {
	var s = d3.event.target.extent();

	svg.selectAll('.articleLine').classed(
	    'active', function(d) { return inBound(d, s); });

	svg.selectAll('.signatureLine').classed(
	    'active', function(d) { return inBound(d, s); });
    }

    articleDivs = articles
	.selectAll('.article')
	.data(data.articles)
	.enter()
	.append('a')
	.attr('href', function(d) { return d.link; })
	.append('div')
	.attr('id', function(d,i) { return 'ar' + i;})
	.classed('article', true)
	.style('width', '300px')
	.style('height', '0px');

    articleDivs.append('h2')
	.text(function(d) {return d.title; });

    articleDivs.append('h3')
	.text(function(d) { return dateFormatter(d.date); });

    articleDivs.append('p')
	.text(function(d) {return d.teaser; });


    function brushend() {
	svg.classed('selecting', !d3.event.target.empty());

	if (d3.event.target.empty()) {
	    return
	};

	var s = d3.event.target.extent();

	articleDivs
	    .transition()
	    .style('height', function(d) {
	    	return inBound(d, s) ? '250px' : '0px';
	    });
    }
    
    svg.call(brush.event);
}
