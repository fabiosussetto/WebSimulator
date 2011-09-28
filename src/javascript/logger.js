(function($) { 
  $(function(){
    // Logger
    $(':text, :password, textarea').live('blur', function(){
      var $this = $(this);
      var builder = new SelectorBuilder();
      var selector = builder.buildPath($this);
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
        _Logger.fill(selector, $this.val(), $.trim(labelText));
      }
    });
    $(':checkbox').click(function(){
      var $this = $(this);
      var builder = new SelectorBuilder();
      var selector = builder.buildPath($this);
      _Logger.checkbox(selector, $this.val());
    });
    $('a').click(function(){
      var $this = $(this);
      var builder = new SelectorBuilder();
      var selector = builder.buildPath($this);
      _Logger.link(selector, $this.text());
    });
    $(':submit').click(function(){
      var $this = $(this);
      var builder = new SelectorBuilder();
      var selector = builder.buildPath($this);
      _Logger.submit(selector, $this.attr('value'));
    });
    
  });
})(jQuery);