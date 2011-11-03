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
      if (labelText) {
        labelText = labelText.replace(/[\s]{2,}/g, ' ');
      }
      return labelText;
    }
    
    $(':text, :password, textarea').live('change', function(){
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
      var labelText = _findLabel($this);
      _Logger.checkbox(selector, labelText);
    });
    
    $(':radio').live('click', function(){
      var $this = $(this);
      var builder = new SelectorBuilder();
      var selector = builder.buildPath($this);
      var labelText = _findLabel($this);
      _Logger.radio(selector, labelText);
    });
    
    $('select').live('change',function(){
      var $this = $(this);
      var builder = new SelectorBuilder();
      var selector = builder.buildPath($this);
      var value = $this.val();
      var displayOption = $('option[value=' + value + ']', $this).text();
      var labelText = _findLabel($this);
      _Logger.select(selector, value, labelText, displayOption);
    });
    
    $('a').each(function(){
      this.addEventListener('click', function(){
        var $this = $(this);
        var builder = new SelectorBuilder();
        var selector = builder.buildPath($this);
        _Logger.link(selector, $this.text().replace(/[\s]{2,}/g, ' '));  
      }, true);
    });
    
    $(':submit, input[type=image], :button').each(function(){
      this.addEventListener('click', function(){
        var $this = $(this);
        var builder = new SelectorBuilder();
        var selector = builder.buildPath($this);
        _Logger.submit(selector, $this.attr('value'));
      }, true);
    });
    
  });
})(jQuery);