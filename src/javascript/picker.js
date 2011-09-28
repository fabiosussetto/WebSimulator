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
  
  $('*').click(function(e){
    if (__pickerEnabled == false) {
      return true;
    }
    e.preventDefault();
    var $this = $(this);
    var builder = new SelectorBuilder();
    var selector = builder.buildPath($this);
    _Picker.setPath(selector, $this[0].tagName, $this.text());
    return false;
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