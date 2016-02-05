var width = 700,//960,
    height = 600,//500,
    fill = d3.scale.category20();

// mouse event vars
var selected_node = null,
    selected_link = null,
    mousedown_link = null;

// init svg
var outer = d3.select("#chart")
  .append("svg:svg")
    .attr("width", width)
    .attr("height", height)
    .attr("pointer-events", "all");

var vis = outer
  .append('svg:g')
    .call(d3.behavior.zoom().on("zoom", rescale));

vis.append('svg:rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', 'white');

// init force layout
var force = d3.layout.force()
    .size([width, height])
    .linkDistance(200)
    //.charge(-200)
    .on("tick", tick);

// get layout properties
var nodes = force.nodes(),
    links = force.links(),
    node = vis.selectAll(".node"),
    link = vis.selectAll(".link"),
    center = parseInt(url("?center"))

$.getJSON( "/static/json/tf_idf_sorted.json", function(data){
  var d = new Object(),i = 0;

  $.each(data, function(key, val){
    cur = {graph_id: val['id']}
    if(val['id'] === center){
      cur.x = width / 2;
      cur.y = height / 2;
      selected_node = cur;
    }
    nodes.push(cur)
    d["id_" + val['id']] = i;
    ++i;
  });

  $.each(data, function(key,val){
    $.each(val['value'], function(key2, val2){
      links.push({
        source: nodes[ d["id_" + val['id']] ],
        target: nodes[ d["id_" + val2['id']] ],
        tfidf: val2['value']
      });
    });
  });

  redraw();
});

// add keyboard callback
//d3.select(window)
//    .on("keydown", keydown);


// focus on svg
// vis.node().focus();

function tick() {
  link.attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });

  node.attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; });
}

// rescale g
function rescale() {
  trans=d3.event.translate;
  scale=d3.event.scale;

  vis.attr("transform",
      "translate(" + trans + ")"
      + " scale(" + scale + ")");
}

// redraw force layout
function redraw() {
  link = link.data(links);

  link.enter().insert("line", ".node")
      .attr("class", "link")
      .on("mousedown",
        function(d) {
          selected_link = d;
          selected_node = null;
          reload_link_info(d);
          /*vis.append("foreignObject")
              //.attr("class", "externalObject")
              .attr("x", (d.source.x - 20) + "px")
              .attr("y", (d.source.y - 40) + "px")
              .attr("width", 200)
              .attr("height", 100)
              .append("xhtml:div")
              .html(d.source.index + " - " + d.target.index);*/
          redraw();
        })

  link.exit().remove();

  link
    .classed("link_selected", function(d) { return d === selected_link; });

  node = node.data(nodes);

  node.enter().insert("circle")
      .attr("class", "node")
      .attr("r", 5)
      .on("mousedown",
        function(d) {
          selected_node = d;
          selected_link = null;
          reload_book_info(d.graph_id);
          /*vis.append("foreignObject")
              //.attr("class", "externalObject")
              .attr("x", (d.x - 20) + "px")
              .attr("y", (d.y - 40) + "px")
              .attr("width", 200)
              .attr("height", 100)
              .append("xhtml:div")
              .html(d.index);*/
          redraw();
        })
    .transition()
      .duration(750)
      .ease("elastic")
      .attr("r", 6.5);

  node.exit().transition()
      .attr("r", 0)
    .remove();

  //console.log("classed");
  //console.log(selected_node);
  node
    .classed("node_selected", function(d) { return d === selected_node; });

  if(d3.event) {
    // prevent browser's default behavior
    d3.event.preventDefault();
  }

  force.start();
}

function reload_book_info(id) {
  $.getJSON( "/static/json/" + id + ".json", function(data){
    var text = 'Title: ' + data['title'] + '</br>\nAuthors:';

    $.each(data['authors'], function(key, val){
      text += ' ' + val['name'];
    });

    text += 'Publisher: ' + data['publisher'] + '</br>';
    text += 'Publication year: ' + data['publication_year'] + '</br>';
    text += 'Description: ' + data['description'] + '</br>';
    text += '<img src=\"' + data['image_url'] + '\" height="500" width="400"></br>'
    text += '<iframe src=\"' + 'https://www.goodreads.com/api/reviews_widget_iframe?isbn=' + data['isbn'] + '\" height=\"500\" width=\"500\"></iframe>'
    $('#book-info').html(text);
  });
}

function append_book_info(id) {
  $.getJSON( "/static/json/" + id + ".json", function(data){
    var text = 'Title: ' + data['title'] + '</br>\nAuthors:';

    $.each(data['authors'], function(key, val){
      text += ' ' + val['name'];
    });

    text += 'Publisher: ' + data['publisher'] + '</br>';
    text += 'Publication year: ' + data['publication_year'] + '</br>';
    text += 'Description: ' + data['description'] + '</br></br>';
    $('#book-info').append(text);
  });
}

function reload_link_info(link){
  var text = 'tf-idf = ' + link.tfidf + '<br/><br/>';
  $('#book-info').html(text);
  append_book_info(link.source.graph_id);
  append_book_info(link.target.graph_id);
}
