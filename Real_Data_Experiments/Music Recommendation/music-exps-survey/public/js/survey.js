$('.next-tab').click(function(){
    $('.nav-tabs > .nav-item > .active').parent().next('li').find('a').trigger('click');
    setTimeout(function(){ 
      $('.tab-content').scrollTop(0);
    }, 0);
});

$('.previous-tab').click(function(){
    $('.nav-tabs > .nav-item > .active').parent().prev('li').find('a').trigger('click');
});

$('.table-striped th').click(function(event) {
    if (!$(event.target).is('input')) {
        $(':checkbox', this).trigger('click');    
    }
});