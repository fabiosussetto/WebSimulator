// Array Remove - By John Resig (MIT Licensed)
Array.prototype.remove = function(from, to) {
  var rest = this.slice((to || from) + 1 || this.length);
  this.length = from < 0 ? this.length + from : from;
  return this.push.apply(this, rest);
};

jQuery.expr[':'].icontains = function(a, i, m) { 
  return jQuery(a).text().toUpperCase().indexOf(m[3].replace(/\+/g, ' ').toUpperCase()) >= 0;
}; 

function SelectorBuilder() {
  
  // Public interface
  
  this.buildPath = function buildPath(elem) {
    var path = [];
    path = _traverse(elem, []); 
    if (path[0][0] == '>') {
      path[0] = path[0].substring(1, path[0].length);
    }
    path = _optimize(elem, path);
    return path.join(" "); 
  }
  
  // Private methods
  
  function _optimize(elem, path) {       
    elem.addClass('__check__');
    for (var i = path.length - 1; i >= 0; i--) {
      var test = path.slice(0);
      var ids = 0;
      $.each(test, function(index, item){
        if (item[0] == '#') ids++; 
      });
      if (test[i][0] == '#') {
        var idElem = $(test[i]);
        if (idElem.is('tr, td')) {
          test.remove(i);
        } else {
          if (ids > 1) {
            $('.__check__').removeClass('__check__');
            return test.slice(i, test.length);
          }
        }
      } else {
        test.remove(i);
      }
      var $selected = $(test.join(' '));
      if ($selected.hasClass('__check__') && $selected.length == 1) {
        path = test;
      }
    }
    $('.__check__').removeClass('__check__');
    return path;
  }
  
  function _traverse(curr_elem, path) {
    if (curr_elem.is('body')) {
      return path;
    }

    var tagName = curr_elem[0].tagName.toLowerCase();          
    var $parent = curr_elem.parent();
    id = curr_elem.attr('id');
    if (id !== undefined) {
      path.unshift('#' + id);
      return _traverse($parent, path);
    }    

    //if ($.inArray(tagName, ['div', 'span', 'p', 'ul', 'ol', 'li']) < 0) {
   
    if (curr_elem.is(':input')) {
      var name = curr_elem.attr('name');
      if (name !== undefined) {
        var inputMatch = tagName + '[name="' + name + '"]';
        path.unshift(inputMatch);    
        return _traverse($parent, path); 
      }     
    }
   
    if (curr_elem.is('a')) {
      var anchorMatch = 'a:icontains(' + curr_elem.text().toLowerCase().replace(/\s/g, '+') + ')';
      path.unshift(anchorMatch);  
      return _traverse($parent, path);
    }
    
    elem_class = curr_elem.attr('class');
    if (elem_class !== undefined && elem_class.length != 0) {     
      if (elem_class.match(/ /)) {
        elem_class = elem_class.split(' ')[0];
      }
      path.unshift('.' + elem_class);   
    } else {                           
      path.unshift(tagName);
    }
    
    if ($(path.join(' '), $parent).length > 1) {
      if (path[0][0] == '.') {
        path[0] = tagName + path[0];
      }    
    }
    
    if ($parent.children(path[0]).length > 1) { 
      index = $parent.children(path[0]).index(curr_elem);      
      path[0] += ':eq(' + index + ')'; 
      path[0] = '> ' + path[0];
    }       

    return _traverse(curr_elem.parent(), path);
  }  
  
}