// Array Remove - By John Resig (MIT Licensed)
Array.prototype.remove = function(from, to) {
  var rest = this.slice((to || from) + 1 || this.length);
  this.length = from < 0 ? this.length + from : from;
  return this.push.apply(this, rest);
};

function SelectorBuilder() {
  
  // Public interface

  this.buildPath = function buildPath(elem) {
    var path = [];
    path = _traverse(elem, []); 
    path = _optimize(elem, path);
    return path.join(" "); 
  }
  
  // Private methods 

  /*function _optimize(curr_elem, path) {
    var last = path.pop();
    var path_try = path;                
    for (var i = path.length - 1; i >= 1; i--){                
      var test = path_try.slice(0, i);    
      console.log('test:' + test.join(' ') + ' ' + last);                     
      if ($(test.join(' ') + ' ' + last).length == 1) {
        path_try.pop();
      } else {
        break;
      }
    };     
    path_try.push(last);
    return path_try;
  } */
  
  function _optimize(curr_elem, path) {       
    //console.log('first: ' + path.join(' '));
    for (var i = path.length - 2; i >= 1; i--) {
      var test = path.slice(0);
      test.remove(i);
      //console.log(test.join(' '));
      if ($(test.join(' ')).length == 1) {
        path = test;
      }
    }
    return path;
  }
  
  function _traverse(curr_elem, path) {
    if (curr_elem.is('body')) {
      return path;
    }

    var tagName = curr_elem[0].tagName.toLowerCase();          

    id = curr_elem.attr('id');
    if (id !== undefined) {
      path.unshift('#' + id);
      //return buildPath(curr_elem.parent(), path); don't stop at first id
      return path;
    }    

    if (curr_elem.is('a')) {
      var anchorMatch = 'a:icontains(' + curr_elem.text().toLowerCase() + ')';
      path.unshift(anchorMatch);  
      if ($(path.join(' ')).length == 1) {   
        //return path;
      }  
      return _traverse(curr_elem.parent(), path);
    }  
    
    if (curr_elem.is('input, select, textarea')) {
      var name = curr_elem.attr('name');
      if (name !== undefined) {
        var inputMatch = tagName + '[name="' + name + '"]';
        path.unshift(inputMatch);    
        if ($(path.join(' ')).length == 1) {
          //return path;
        }
        return _traverse(curr_elem.parent(), path); 
      }     
    }
                 
    elem_class = curr_elem.attr('class');
    if (elem_class !== undefined && elem_class.length != 0) {     
      if (elem_class.match(/ /)) {
        elem_class = elem_class.split(' ')[0];
      }
      path.unshift('.' + elem_class);   
    } else {                           
      if ($.inArray(tagName, ['div', 'span', 'p', 'ul', 'ol', 'li']) < 0) {
        path.unshift(tagName);
      } else {
        //return _traverse(curr_elem.parent(), path);
      }
    }  
    
    var $parent = curr_elem.parent();
    //console.debug('curr path: ' + path);
    if ($(path.join(' '), $parent).length > 1) { 
      index = curr_elem.index();      
      //console.debug(curr_elem);
      //console.debug($parent.children());
      
      index = $parent.find(curr_elem[0].tagName).index(curr_elem);
      path[path.length - 1] += ':eq(' + index + ')'; 
    }        

    /*if ($parent.find(path.join(' ')).length > 1) {
      path.unshift('>'); 
    }*/
    
    if ($(path.join(' ')).length == 1) {
      //return path;
    }
    return _traverse(curr_elem.parent(), path);
  }  
  
}
  

  
jQuery.expr[':'].icontains = function(a, i, m) { 
  return jQuery(a).text().toUpperCase().indexOf(m[3].toUpperCase()) >= 0; 
};   
