var center = center = parseInt(url("?center"));
var g = {
   nodes: [],
   edges: []
};

s = new sigma({
  graph: g,
  container: 'all-chart',
  renderer: {
    container: document.getElementById('all-chart'),
    type: 'canvas'
  },
  settings: {
    edgeLabelSize: 'proportional',
    maxNodeSize: 2,
    zoomMax: 4
 }
});

var selected_node = null;

sigma.parsers.json(
  '/all_graph_json',
  s,
  function() {
    var i,nodes = s.graph.nodes(),len = nodes.length;

    for(i = 0; i < len; i++){
      if(s.graph.degree(nodes[i].id) == 0){
        s.graph.dropNode(nodes[i].id);
      }else{
       nodes[i].x = Math.random();
       nodes[i].y = Math.random();
       nodes[i].size = s.graph.degree(nodes[i].id);
       nodes[i].color = '#ec5148';

       if(nodes[i].id == center){
         selected_node = nodes[i];
         nodes[i].color = '#333'
       }
     }
    }

    // Refresh the display:
    s.refresh();

    s.bind('clickNode', function(e){
      var id = e.data.node.id;
      e.data.node.color = '#333';
      if(selected_node != null)
        selected_node.color = '#ec5148';
      s.refresh();
      selected_node = e.data.node;
      reload_book_info(id);
    });

    // ForceAtlas Layout
    s.startForceAtlas2();

    var isRunning = true;
    document.getElementById('stop-layout').addEventListener('click',function(){
      if(isRunning){
        isRunning = false;
        s.stopForceAtlas2();
        $('#stop-layout').html('Start Graph');
      }else{
        isRunning = true;
        s.startForceAtlas2();
        $('#stop-layout').html('Stop Graph');
      }
    },true);
  }
);

function reload_book_info(id) {
  $.getJSON( "/book_json?id=" + id, function(data){
    $('#book-title').html(data['title']);
    $('#book-description').html(data['description']);

    var authors = '';
    $.each(data['authors'], function(key, val){
      authors += ' ' + val['name'];
    });
    $('#book-authors').html(authors);

    $('#book-publisher').html(data['publisher']);
    $('#book-publication-year').html(data['publication_year']);
    $('#book-img').attr('src', data['image_url']);
  });
}
