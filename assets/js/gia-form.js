/*
    By Osvaldas Valutis, www.osvaldas.info
    Available for use under the MIT License
*/

'use strict';

;( function( $, window, document, undefined )
{
    $( '.gia-image-field' ).each( function()
    {
        var $input   = $( this ).find('input'),
            $label   = $( this ).find( 'label span' ),
            labelVal = $label.html();

        $input.on( 'change', function( e )
        {
            var fileName = '';

            if( e.target.value )
                fileName = e.target.value.split( '\\' ).pop();

            if( fileName )
                $label.html( fileName );
            else
                $label.html( labelVal );
        });

        // Firefox bug fix
        $input
        .on( 'focus', function(){ $input.addClass( 'has-focus' ); })
        .on( 'blur', function(){ $input.removeClass( 'has-focus' ); });
    });


})( jQuery, window, document );


// Hide/Show Other Category
$(function() {

    $('#other_category_field').hide();

    var text = "Other";
    var value = $("option").filter(function() {
      return $(this).text() === text;
    }).first().attr("value");

    console.log(value);


    $('#id_category').change(function(){
        if( $('#id_category').val() == value ) {
            $('#other_category_field').show();
        } else {
            $('#other_category_field').hide();
        }
    });
});
