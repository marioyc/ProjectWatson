var center = center = parseInt(url("?center"));
var g = {
   nodes: [],
   edges: []
};

s = new sigma({
  graph: g,
  container: 'chart',
  renderer: {
    container: document.getElementById('chart'),
    type: 'canvas'
  },
  /*settings: {
   minNodeSize: 8,
   maxNodeSize: 16
 }*/
});

var selected_node;

sigma.parsers.json(
  '/graph_json?center=' + center,
  s,
  function() {
    var i,nodes = s.graph.nodes(),len = nodes.length;

    for(i = 0; i < len; i++){
       nodes[i].x = Math.random();
       nodes[i].y = Math.random();
       nodes[i].size = s.graph.degree(nodes[i].id);
       nodes[i].color = '#ec5148';

       if(nodes[i].id == center){
         selected_node = nodes[i];
         nodes[i].color = '#333'
       }
    }

    // Refresh the display:
    s.refresh();

    s.bind('clickNode', function(e){
      var id = e.data.node.id;
      e.data.node.color = '#333';
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
    var text = '<table class="table table-striped"><tbody><tr><td><h4>' + data['title'] + '</h4></td></tr>';
    text += '<tr><td>' + data['description'] + '</td></tr>';
    text += '<tr><td>Authors:';

    $.each(data['authors'], function(key, val){
      text += ' ' + val['name'];
    });

    text += '</td></tr> <tr><td>Publisher: ' + data['publisher'] + '</td></tr>';
    text += '<tr><td>Publication year: ' + data['publication_year'] + '</td></tr>';
    text += '<tr><td><img src=\"' + data['image_url'] + '\" height="400" width="300"></td></tr>'
    text += '</tbody></table>';

    $('#book-info-table').html(text);
    $('#book-comments').html('<iframe src=\"' + 'https://www.goodreads.com/api/reviews_widget_iframe?isbn=' + data['isbn'] + '\" height=\"1000\"></iframe>');
  });
}

function append_book_info(id) {
  $.getJSON( "/book_json?id=" + id, function(data){
    var text = 'Title: ' + data['title'] + '</br>\nAuthors:';

    $.each(data['authors'], function(key, val){
      text += ' ' + val['name'];
    });

    text += 'Publisher: ' + data['publisher'] + '</br>';
    text += 'Publication year: ' + data['publication_year'] + '</br>';
    text += 'Description: ' + data['description'] + '</br></br>';
    $('#book-info-table').append(text);
    $('#book-comments').append('<iframe src=\"' + 'https://www.goodreads.com/api/reviews_widget_iframe?isbn=' + data['isbn'] + '\" height=\"500\"></iframe>');
  });
}

function reload_link_info(link){
  var text = 'tf-idf = ' + link.tfidf + '<br/><br/>';
  $('#book-info-table').html(text);
  $('#book-comments').html('');
  append_book_info(link.source.graph_id);
  append_book_info(link.target.graph_id);
}
