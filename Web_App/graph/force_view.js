var width = 960,
    height = 500,
    fill = d3.scale.category20();

// mouse event vars
var selected_node = null,
    selected_link = null,
    mousedown_link = null,
    mousedown_node = null,
    mouseup_node = null;

// init svg
var outer = d3.select("#chart")
  .append("svg:svg")
    .attr("width", width)
    .attr("height", height)
    .attr("pointer-events", "all");

var vis = outer
  .append('svg:g')
    .call(d3.behavior.zoom().on("zoom", rescale))
    .on("dblclick.zoom", null)
  .append('svg:g')
    .on("mousemove", mousemove)
    .on("mousedown", mousedown)
    .on("mouseup", mouseup);

vis.append('svg:rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', 'white');

// init force layout
var force = d3.layout.force()
    .size([width, height])
    .linkDistance(80)
    //.charge(-200)
    .on("tick", tick);

// get layout properties
var nodes = force.nodes(),
    links = force.links(),
    node = vis.selectAll(".node"),
    link = vis.selectAll(".link");

nodes.push({name:"Center"})
/*nodes.push({})
nodes.push({})
nodes.push({})*/

/*links.push({source:nodes[1], target:nodes[2]});
links.push({source:nodes[0], target:nodes[2]});
links.push({source:nodes[0], target:nodes[1]});*/

for(var i = 1;i < 50;++i){
  nodes.push({})
  links.push({source:nodes[0], target:nodes[i]})
}

/*for(var i = 0;i < 40;++i){
  nodes.push({})
}

for(var i = 0;i < 40;++i){
  links.push({source:nodes[50 + i], target:nodes[50 + (i + 1) % 40]})
}*/

/*for(var i = 0;i < 50;++i){
  nodes.push({})
}

for(var i = 0;i < 50;++i){
  links.push({source:nodes[90 + i], target:nodes[90 + (i + 1) % 50]})
}*/

// add keyboard callback
//d3.select(window)
//    .on("keydown", keydown);

redraw();

// focus on svg
// vis.node().focus();

function mousedown() {
  if (!mousedown_node && !mousedown_link) {
    // allow panning if nothing is selected
    vis.call(d3.behavior.zoom().on("zoom"), rescale);
    return;
  }
}

function mousemove() {
  if (!mousedown_node) return;

  // update drag line
}

function mouseup() {
  /*if (mousedown_node) {
    if (!mouseup_node) {
      // add node
      var point = d3.mouse(this),
        node = {x: point[0], y: point[1]},
        n = nodes.push(node);

      // select new node
      selected_node = node;
      selected_link = null;

      // add link to mousedown node
      links.push({source: mousedown_node, target: node});
    }

    redraw();
  }*/
  // clear mouse event vars
  resetMouseVars();
}

function resetMouseVars() {
  mousedown_node = null;
  mouseup_node = null;
  mousedown_link = null;
}

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
          mousedown_link = d;
          if (mousedown_link == selected_link) selected_link = null;
          else selected_link = mousedown_link;
          selected_node = null;

          vis.append("foreignObject")
              //.attr("class", "externalObject")
              .attr("x", (d.source.x - 20) + "px")
              .attr("y", (d.source.y - 40) + "px")
              .attr("width", 200)
              .attr("height", 100)
              .append("xhtml:div")
              .html(d.source.index + " - " + d.target.index);

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
          //console.log(d);
          // disable zoom
          vis.call(d3.behavior.zoom().on("zoom"), null);

          mousedown_node = d;
          if (mousedown_node == selected_node) selected_node = null;
          else selected_node = mousedown_node;
          selected_link = null;

          //lineID = d3.select(this).attr("index");
          //svg.append("foreignObject")
          //vis.append("svg:svg")
          vis.append("foreignObject")
              //.attr("class", "externalObject")
              .attr("x", (d.x - 20) + "px")
              .attr("y", (d.y - 40) + "px")
              .attr("width", 200)
              .attr("height", 100)
              .append("xhtml:div")
              .html(d.index);

          redraw();
        })
      .on("mousedrag",
        function(d) {
          // redraw();
        })
      .on("mouseup",
        function(d) {
          if (mousedown_node) {
            mouseup_node = d;
            if (mouseup_node == mousedown_node) { resetMouseVars(); return; }

            // add link
            //var link = {source: mousedown_node, target: mouseup_node};
            //links.push(link);

            // select new link
            selected_link = link;
            selected_node = null;

            // enable zoom
            vis.call(d3.behavior.zoom().on("zoom"), rescale);
            redraw();
          }
        })
    .transition()
      .duration(750)
      .ease("elastic")
      .attr("r", 6.5);

  node.exit().transition()
      .attr("r", 0)
    .remove();

  node
    .classed("node_selected", function(d) { return d === selected_node; });



  if (d3.event) {
    // prevent browser's default behavior
    d3.event.preventDefault();
  }

  force.start();
  //console.log(force.nodes());
  //console.log(force.links());
}

/*function spliceLinksForNode(node) {
  toSplice = links.filter(
    function(l) {
      return (l.source === node) || (l.target === node); });
  toSplice.map(
    function(l) {
      links.splice(links.indexOf(l), 1); });
}

function keydown() {
  if (!selected_node && !selected_link) return;
  switch (d3.event.keyCode) {
    case 8: // backspace
    case 46: { // delete
      if (selected_node) {
        nodes.splice(nodes.indexOf(selected_node), 1);
        spliceLinksForNode(selected_node);
      }
      else if (selected_link) {
        links.splice(links.indexOf(selected_link), 1);
      }
      selected_link = null;
      selected_node = null;
      redraw();
      break;
    }
  }
}*/