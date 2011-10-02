(function($) { 
  $(function(){
    // Logger
    
    function _findLabel(element) {
      var labelText = null;
      var id = element.attr('id');
      var $label = null;
      if (id !== undefined) {
        $label = $('label[for=' + id + ']'); 
        if ($label.length) {
          labelText = $label.text();  
        } else { 
          $label = element.closest('label')
          if ($label.length) {
            labelText = $label.text();
          }
        }
      }
      return labelText;
    }
    
    $(':text, :password, textarea').live('blur', function(){
      var $this = $(this);
      var builder = new SelectorBuilder();
      var selector = builder.buildPath($this);
      var val = $this.val();
      
      if (val.length > 0) {
        labelText = _findLabel($this);
        _Logger.fill(selector, $this.val(), $.trim(labelText));
      }
    });
    
    $(':checkbox').live('click', function(){
      var $this = $(this);
      var builder = new SelectorBuilder();
      var selector = builder.buildPath($this);
      _Logger.checkbox(selector, $this.val());
    });
    
    $('select').live('change',function(){
      var $this = $(this);
      var builder = new SelectorBuilder();
      var selector = builder.buildPath($this);
      var value = $this.val();
      var displayOption = $('option[value=' + value + ']', $this).text();
      labelText = _findLabel($this);
      _Logger.select(selector, value, labelText, displayOption);
    });
    
    $('a').live('click', function(){
      var $this = $(this);
      var builder = new SelectorBuilder();
      var selector = builder.buildPath($this);
      _Logger.link(selector, $this.text());
    });
    
    $(':submit').live('click', function(){
      var $this = $(this);
      var builder = new SelectorBuilder();
      var selector = builder.buildPath($this);
      _Logger.submit(selector, $this.attr('value'));
    });
    
  });
})(jQuery);