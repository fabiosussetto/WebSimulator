function SelectorBuilder() {
  
  // Public interface

  this.buildPath = function buildPath(elem) {
    var path = [];
    path = _traverse(elem, []);
    return path.join(" "); 
  }
  
  // Private methods
  
  function _traverse(curr_elem, path) {
    if (curr_elem.is('body')) {
      return path;
    }
    id = curr_elem.attr('id');
    if (id !== undefined) {
      path.unshift('#' + id);
      //return buildPath(curr_elem.parent(), path); don't stop at first id
      return path;
    }
                           
    elem_class = curr_elem.attr('class');
    if (elem_class !== undefined) {     
      if (elem_class.match(/ /)) {
        elem_class = elem_class.split(' ')[0];
      }
      path.unshift('.' + elem_class);   
    } else {
      path.unshift(curr_elem[0].tagName);  
    }  

    if (curr_elem.parent().children(curr_elem[0].tagName).length > 1) {
      index = curr_elem.index() + 1;  
      path[0] = path[0] + ':nth-child(' + index + ')'; 
    }        

    if (curr_elem.parent().find(path.join(' ')).length > 1) {
      path.unshift('>'); 
    }
       
    return _traverse(curr_elem.parent(), path);
  }
  
}
  
