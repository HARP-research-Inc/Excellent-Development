$(function() {
    var expanded = true;
    var oldWidth = $("#main-box").width();
    var oldHeight = $("#main-box").height();
    var oldPadding = $("#main-box").css('padding');
    var cornerWidth = $("#corner-box").outerWidth();
    var cornerHeight = $("#corner-box").outerHeight();
    var minWidth, minHeight;

    function setMinSize() {
        minWidth = cornerWidth + 103 + $("#collapse-button").outerWidth();
        minHeight = cornerHeight +8;
        $("#main-box").resizable("option", "minWidth", minWidth);
        $("#main-box").resizable("option", "minHeight", minHeight);
    }

    $("#main-box").draggable().resizable();
    setMinSize();

    $("#corner-box").on('click', function() {
        var width = $(this).outerWidth();
        var height = $(this).outerHeight();
        $(this).hide();
        $("#corner-input").css({width: width, height: height}).val($(this).find('span').text().trim()).show().focus();
        setMinSize();
    });

    $("#corner-input").on('focusout', function() {
        $(this).hide();
        $("#corner-box").show().find('span').text($(this).val());
        setMinSize();
    });

    $('#corner-input').on('keyup', function(e){
        if (e.key === 'Enter' || e.keyCode === 13){
            $(this).trigger('focusout');
        }
    });
    $("#collapse-button").on('click', function(e) {
        e.stopPropagation();
        if (expanded) {
            oldWidth = $("#main-box").width();
            oldHeight = $("#main-box").height();
            $(this).fadeOut(250, function() {
                $("#corner-box").animate({
                    width: minWidth,
                    height: minHeight,
                }, 250, function() {
                    $("#main-box").animate({
                        width: minWidth,
                        height: minHeight,
                    }, 250, function() {
                        $(this).css({
                            padding: 0,
                        }).resizable( "disable" );
                    });
                });
                $("#expand-button").show();
            });
            expanded = false;
        }
    });

    $("#expand-button").on('click', function(e) {
        e.stopPropagation();
        if (!expanded) {
            $("#main-box").css({
                padding: oldPadding,
            });
            $("#corner-box").animate({
                width: cornerWidth,
                height: cornerHeight,
            }, 250, function() {
                $("#main-box").animate({
                    width: oldWidth,
                    height: oldHeight,
                }, 250, function() {
                    $(this).resizable("enable");
                });
            });
            $(this).hide();
            $("#collapse-button").show();
            expanded = true;
        }
        setMinSize();
    });
});