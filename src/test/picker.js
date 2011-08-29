(function($) {
$(function(){

function Overlay(width, height, left, top) {

  this.width = this.height = this.left = this.top = 0;

  // outer parent
  var outer = $("<div class='outer' />").appendTo("body");
  
  // red lines (boxes)
  var topbox    = $("<div style='position:absolute; background:rgb(255,0,0); z-index:65000;' />").css("height", 1).appendTo(outer);
  var bottombox = $("<div style='position:absolute; background:rgb(255,0,0); z-index:65000;' />").css("height", 1).appendTo(outer);  
  var leftbox   = $("<div style='position:absolute; background:rgb(255,0,0); z-index:65000;' />").css("width",  1).appendTo(outer);
  var rightbox  = $("<div style='position:absolute; background:rgb(255,0,0); z-index:65000;' />").css("width",  1).appendTo(outer);
  
  // don't count it as a real element
  outer.mouseover(function(){ 
      outer.hide(); 
  });

/**
 * Public interface
 */
  
    this.resize = function resize(width, height, left, top) {
      if (width != null)
        this.width = width;
      if (height != null)
        this.height = height;
      if (left != null)
        this.left = left;
      if (top != null)
        this.top = top;      
    };
 
    this.show = function show() {
       outer.show();
    };
             
    this.hide = function hide() {
       outer.hide();
    };     

    this.render = function render(width, height, left, top) {
      this.resize(width, height, left, top);
      topbox.css({
        top:   this.top,
        left:  this.left,
        width: this.width
      });
      bottombox.css({
        top:   this.top + this.height - 1,
        left:  this.left,
        width: this.width
      });
      leftbox.css({
        top:    this.top, 
        left:   this.left, 
        height: this.height
      });
      rightbox.css({
        top:    this.top, 
        left:   this.left + this.width - 1, 
        height: this.height  
      });
        
      this.show();
    };      
    // initial rendering [optional]
    //this.render(width, height, left, top);
  }
    
  
  // test
  var box = new Overlay(200, 200, 400, 20);
  
  __pickerEnabled = false;
  
  $("body").mouseover(function(e){
    if (__pickerEnabled == false) {
      box.hide();
      return true;
    }
    var el = $(e.target);
    var offset = el.offset();
    box.render(el.outerWidth(), el.outerHeight(), offset.left, offset.top);
  });
  
  //$('#sidebar ul li:nth-child(0)').css('border', '1px solid green'); 

  $('*').click(function(e){
    if (__pickerEnabled == false) {
      return true;
    }
    e.preventDefault();
    var path = [];
    
    var $this = $(this);
    path = buildPath($this, path);
    //console.debug(path.join(' '));  
    //alert(path.join(' '));
    pickedPath = path.join(' ')
    _Picker.setPath(pickedPath, $this[0].tagName, $this.text());
		//$('.selected').removeClass('selected');
		//$(path.join(' ')).addClass('selected');
    return false;
  });   

  function buildPath(curr_elem, path) {
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
       
    return buildPath(curr_elem.parent(), path); 
  }
  
  // Logger
  
  $(':text, :password, textarea').live('blur', function(){
    var $this = $(this);
    var path = buildPath($this, []);
    var val = $this.val();
    var labelText = "";
    var $label = null;
    
    var id = $this.attr('id');
    if (id !== undefined) {
      $label = $('label[for=' + id + ']'); 
      if ($label.length) {
        labelText = $label.text();  
      } else { 
        $label = $this.closest('label')
        if ($label.length) {
          labelText = $label.text();
        }
      }
    }
    if (val.length > 0) {
      _Logger.fill(path, $this.val(), $.trim(labelText));
    }
  });
  $(':checkbox').click(function(){
    var $this = $(this);
    var path = buildPath($this, []);
    _Logger.checkbox(path.join(' '), $this.val());
  });
  $('a').click(function(){
    var $this = $(this);
    var path = buildPath($this, []);
    _Logger.link(path.join(' '), $this.text());
  });
  $(':submit').click(function(){
    var $this = $(this);
    var path = buildPath($this, []);
    _Logger.submit(path.join(' '), $this.attr('value'));
  });
  
  // Assertions
  function Assertion() {
    
    this.contentMatch = function contentMatch(text, selector) {
      var element = $(selector);
      if (element.length === 0) {
        return false;
      }
      regex = new RegExp(text, "i");
      return regex.test(element.text());
    }; 
  }
  
  _assert = new Assertion();
  
});

})(jQuery);


