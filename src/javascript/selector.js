// Array Remove - By John Resig (MIT Licensed)
Array.prototype.remove = function(from, to) {
  var rest = this.slice((to || from) + 1 || this.length);
  this.length = from < 0 ? this.length + from : from;
  return this.push.apply(this, rest);
};

jQuery.expr[':'].icontains = function(a, i, m) { 
  return jQuery(a).text().toUpperCase().indexOf(m[3].replace(/\+/g, ' ').toUpperCase()) >= 0; 
}; 

(function($) {

  function SmartSelector() {
    // Public interface
    
    weighed = [];
    originalPath = null;
    
    this.select = function smartSelect(selector) {
      return tryGet(selector);
    };
    
    this.get = function() {
      return weighed;  
    };
    
    // Private methods
    
    function tryGet(selector) {
      var originalSelector = selector;
      var path = selector.split(' ');
      if (path.length === 1) {
        return $(originalSelector);
      }
      originalPath = path;
      
      for (i = 0; i < path.length - 1; i++) {
        buildItem(i, path[i]);
      }
      
      var arr = weighed;
      while (arr.length > 0) {
        var path = joinPath(arr);
        var test = $(path); 
        if (test.length > 0) {
          return test;
        }
        arr = removeMax(arr);
      }
      
      // try at least with the remaining element
      test = $(originalPath[originalPath.length - 1]);
      if (test.length > 0) {
        return test;
      }
      
      // no element has been found 
      return $([]);
    };
    
    function removeMax(arr) {
      var max = 0;
      var maxIndex = 0;
      for (i = 0; i < arr.length; i++) {
        if (arr[i].weight > max) {
          max = arr[i].weight;
          maxIndex = i;
        }
      }
      arr.remove(maxIndex);
      return arr;
    };
    
    function joinPath(arr) {
      path = [];
      for (i = 0; i < arr.length; i++) {
        path.push(arr[i].item);
      } 
      path.push(originalPath[originalPath.length - 1]);
      return path.join(" ").replace(/_\|_/, " ");
    } 
    
    function check(path) {
      return $(path).length > 0;
    }; 
    
    function buildItem (index, item) {
      if (item === '>') return false;
      weighed.push({
        item : item,
        weight : getWeight(index, item)
      });
    };
    
    function getWeight(index, item) {
      index++;
      if (item[0] === '#') {
        return 1 * index;
      }
      if (item.indexOf('.') !== 0) {
        return 10 * index;
      }
      if (item[0] === '.') {
        return 50 * index;
      }
      return 100 * index;
    };
    
  }

  $.smartSelector = new SmartSelector();

})(jQuery);