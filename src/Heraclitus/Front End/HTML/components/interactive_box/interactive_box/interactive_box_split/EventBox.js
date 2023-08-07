class EventBox extends ResizableBox {
    constructor(boxId, title, mainColor, secondaryColor, tertiaryColor, parentBox = null, jsonChildren = null) {
        super(boxId, title, mainColor, secondaryColor, tertiaryColor, parentBox, jsonChildren);
    }

    attachEvents() {
        super.attachEvents();
        var box = this;
        var parentId = this.parentBox;
        var oldWidth = $("#" + this.boxId).width();
        var oldHeight = $("#" + this.boxId).height();
        var oldPadding = $("#" + this.boxId).css('padding');
        var cornerWidth = $("#" + this.boxId + "-corner-box").outerWidth();
        var cornerHeight = $("#" + this.boxId + "-corner-box").outerHeight();
        var minWidth, minHeight;
        var boxId = this.boxId;  // store the boxId in a variable
        var parentId = this.parentId;
        var mainColor = this.mainColor; // store the mainColor in a variable
        var secondaryColor = this.secondaryColor; // store the secondaryColor in a variable
        var tertiaryColor = this.tertiaryColor; // store the tertiaryColor in a variable
        var initialCollapse = true;  // flag to indicate whether this is the initial collapse

        const setMinSize = () => {
            minWidth = cornerWidth + 103 + $("#" + boxId + "-collapse-button").outerWidth();
            minHeight = cornerHeight + 8;
            $("#" + boxId).resizable("option", "minWidth", minWidth);
            $("#" + boxId).resizable("option", "minHeight", minHeight);
        };

        $("#" + boxId).resizable({
            resize: function(event, ui) {
              // calculate the new size of the parent box based on the resized child box
              let childBoxSize = box.calculateChildBoxSize(boxId, box.childBoxes);
              // get the parent box size
              let parentBoxSize = { width: $(this).parent().width(), height: $(this).parent().height() };
              // define a margin
              let margin = 10; 
          
              // check if the child box is near the edge of the parent box
              if (childBoxSize.totalWidth + margin >= parentBoxSize.width ||
                  childBoxSize.totalHeight + margin >= parentBoxSize.height) {
                // expand the parent box
                $(this).parent().css({
                  width: childBoxSize.totalWidth + 2 * margin,
                  height: childBoxSize.totalHeight + 2 * margin
                });
              }
          
              // update oldWidth and oldHeight
              box.oldWidth = ui.size.width;
              box.oldHeight = ui.size.height;
              $("#" + parentId).shrinkToChildBoxSize()
            }
          });
          
          
          
        $("#" + parentId).droppable({
            accept: function(draggable) {
                // Only accept draggable if this box is expanded or the draggable is the background
                return $(this).hasClass('expanded') || draggable.attr('id') === 'background';
            },
            drop: function(event, ui) {
                var dropped = ui.helper;
                var droppedOn = $(this);
                if (droppedOn.hasClass('collapsed')) {
                    // If the box is collapsed, find the box beneath it and drop on that instead
                    var beneathBox = droppedOn.parent().closest('.interactive-box');
                    if (beneathBox.length > 0) {
                        droppedOn = beneathBox;
                    }
                }
                if (droppedOn.attr('id') === 'body') { //if (droppedOn.attr('id') === 'edit_plane') {
                    $(dropped).detach().css({top: 0,left: 0}).appendTo(droppedOn);
                    $(dropped).removeChildBox().css({top: 0,left: 0});
                } else {
                    $(dropped).detach().css({top: 0,left: 0}).appendTo(droppedOn);
                    $(dropped).addChildBox(droppedOn);
                    $(dropped).removeChildBox().css({top: 0,left: 0});
                }
            }
        });        
        
        $("#" + boxId).draggable({
            handle: "#" + boxId + "-corner-box" + " .drag-handle",
            helper: "clone",
            appendTo: 'body',
            start: function() {
                $(this).css({
                    'opacity': '0.2'
                });
                // Temporarily disable droppable functionality for this item
                $(this).droppable('disable');
            },    
            stop: function(event, ui) {
                $(this).css({ 'opacity': '1' });

                // Temporarily hide the draggable element
                $(this).hide();

                // Now when you call elementFromPoint, it will return the underlying element
                var droppedOn = $(document.elementFromPoint(event.clientX, event.clientY));

                // If the droppedOn element is a drag handle, get its parent interactive box
                if (droppedOn.hasClass('drag-handle')) {
                    droppedOn = droppedOn.closest('.interactive-box');
                }

                // Make the draggable element visible again
                $(this).show();

                // Re-enable droppable functionality for this item
                $(this).droppable('enable');

                if (droppedOn[0].nodeName === "BODY" || droppedOn.hasClass('your-container-class')) {
                    console.log("Dropped on the body or specific container");
                    $(this).detach().css({top: 0,left: 0}).appendTo('body');
                } else if (droppedOn.hasClass('interactive-box')) {
                    console.log("Dropped on another interactive box: "+droppedOn[0].boxId); //WORK ON MEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
                    $(this).detach().css({top: 0,left: 0}).appendTo(droppedOn);
                }
            }

        }).resizable();

        
        $("#" + boxId).click(function() {
            // Bring the clicked box to the front by setting its z-index to the maximum z-index plus one
            var maxZ = Math.max.apply(null, $.map($('body > *'), function(e,n) {
                if ($(e).css('position') != 'static')
                    return parseInt($(e).css('z-index')) || 1;
            }));
            $(this).css('z-index', maxZ + 1);
        });        
        
        setMinSize();

        $("#" + boxId + "-corner-box span").on('click', function() {
            var width = $(this).parent().outerWidth() - 20;  // reduce the width by the width of the drag handle
            var height = $(this).parent().outerHeight();
            $(this).parent().hide();
            $("#" + boxId + "-corner-input").css({width: width, height: height}).val($(this).text().trim()).show().focus();
            setMinSize();
        });
        

        $("#" + boxId + "-corner-input").on('focusout', function() {
            let newTitle = $(this).val();
            $(this).hide();
        
            // Create a new InteractiveBox object with the new title
            let newBox = new InteractiveBox(boxId, newTitle, mainColor, secondaryColor, tertiaryColor);
        
            // Generate the new box's HTML and replace the old box in the DOM
            let newBoxHTML = newBox.generateHTML();
            $("#" + boxId).replaceWith(newBoxHTML);
        
            // Apply dynamic styles and attach events to the new box
            newBox.applyDynamicStyles();
            newBox.attachEvents();
        });

        $("#" + boxId + "-corner-input").on('keyup', function(e) {
            if (e.key === 'Enter' || e.keyCode === 13) {
                $(this).trigger('focusout');
            }
        });
        
        this.updateCollapseExpandEvents();  // Use the new method here

        $("#" + this.boxId + "-collapse-button").click();  // trigger the initial collapse
    }
    
    childBoxExpanded(childBox) {
        // Recalculate oldWidth and oldHeight based on the expanded child box
        console.log("'"+childBox.boxId+ "' called size update for '"+this.boxId+"'");
       
        // Generate the new collapse and expand events
        const {collapseEvent, expandEvent} = this.generateCollapseExpandEvents();
        if (childBox.parentBox != null) {
            $("#" + this.boxId + "-expand-button").click();  // trigger a click event on the expand button
        }     
    }
    
    childBoxShrunk(childBox) {
        console.log("'" + childBox.boxId + "' called size update for '" + this.boxId + "'");
        
        // Generate the new collapse and expand events
        const {collapseEvent, expandEvent} = this.generateCollapseExpandEvents();
        if (childBox.parentBox != null) {
            //$("#" + this.boxId + "-expand-button").click();  // trigger a click event on the collapse button
        }        
    }

    generateCollapseExpandEvents() {
        var box = this;
        var expanded = this.expanded;
        var oldWidth = $("#" + this.boxId).width();
        var oldHeight = $("#" + this.boxId).height();
        var oldPadding = $("#" + this.boxId).css('padding');
        var cornerWidth = $("#" + this.boxId + "-corner-box").outerWidth();
        var cornerHeight = $("#" + this.boxId + "-corner-box").outerHeight();
        var minWidth, minHeight;
        var boxId = this.boxId;  // store the boxId in a variable
        var parentBox = this.parentBox;
        var mainColor = this.mainColor; // store the mainColor in a variable
        var secondaryColor = this.secondaryColor; // store the secondaryColor in a variable
        var tertiaryColor = this.tertiaryColor; // store the tertiaryColor in a variable
        var initialCollapse = true;  // flag to indicate whether this is the initial collapse
        
        var setMinSize = () => {
            minWidth = cornerWidth + 103 + $("#" + boxId + "-collapse-button").outerWidth();
            minHeight = cornerHeight + 8;
            $("#" + boxId).resizable("option", "minWidth", minWidth);
            $("#" + boxId).resizable("option", "minHeight", minHeight);
        };

        setMinSize();
        console.log("is expanded: " + this.expanded);
        var collapseEvent = (e) => {
            e.stopPropagation();
            if (expanded) {
                var collapsedSize = this.calculateCollapsedSize();
                this.oldWidth = oldWidth = minWidth;
                this.oldHeight = oldHeight = minHeight;
                expanded = false;
                this.expanded = expanded; // Update the expanded property
                if (initialCollapse) {
                    $("#" + boxId + "-corner-box").css({
                        width: collapsedSize.collapsedWidth,
                        height: collapsedSize.collapsedHeight
                    });
                    $("#" + boxId + "-expand-button").css("color", tertiaryColor).show();
                    $("#" + boxId).css({
                        width: collapsedSize.collapsedWidth,
                        height: collapsedSize.collapsedHeight,
                        padding: 0
                    }).resizable("disable");
                    $("#" + boxId + " > .interactive-box").hide();  // hide only direct child boxes
                    initialCollapse = false;
                } else {
                    $(this).fadeOut(250, function() {
                        $("#" + boxId + "-corner-box").animate({
                            width: minWidth,
                            height: minHeight,
                        }, 250, function() {
                            $("#" + boxId + "-expand-button").css("color", tertiaryColor).show();
                            $("#" + boxId).animate({
                                width: minWidth,
                                height: minHeight,
                            }, 250, function() {
                                $(this).css({
                                    padding: 0,
                                }).resizable( "disable" );
                                $("#" + boxId + " > .interactive-box").hide();  // hide only direct child boxes
                                if (parentBox != null){
                                    parentBox.shrinkToChildBoxSize();
                                }
                            });
                        });
                    });
                }
                $("#" + boxId).addClass('collapsed'); // add the collapsed class when the box is collapsed
            }            
        };
        
        var expandEvent = (e) => {
            var generateChildBoxes = this.generateChildBoxes;
            var thisBox = this;
            var boxId = this.boxId;
            var childBoxes = this.childBoxes;
            //this.childBoxSize = childBoxSize;
            e.stopPropagation();
            generateChildBoxes(boxId, childBoxes);
            childBoxSize = this.childBoxSize = this.calculateChildBoxSize(boxId, childBoxes)
            
            $("#" + boxId).show(0, (e) => {  // add a callback function here
                $("#" + boxId + " > .interactive-box").show()  // change this line
                if (childBoxSize.totalWidth > 0 && childBoxSize.totalHeight > 0) {
                    oldWidth = Math.max(oldWidth, childBoxSize.totalWidth);
                    oldHeight = Math.max(oldHeight, childBoxSize.totalHeight+20);
                };
                this.oldWidth = oldWidth;
                this.oldHeight = oldHeight;
                expanded = true;
                this.expanded = expanded; // Update the expanded property
                if (parentBox != null){
                    parentBox.childBoxExpanded(thisBox)
                }
                // If this is the first time the box is being expanded and it has JSON children, parse them
                // If this is the first time the box is being expanded and it has JSON children, parse them
                if (!this.expanded && this.jsonChildren) {
                    this.parseJsonToInteractiveBoxes(this.jsonChildren);
                    this.jsonChildren = null;  // Clear the JSON children to prevent them from being parsed again
                }

                console.log("'"+this.boxId+"' has oldHeight "+oldHeight);
                $("#" + boxId).css({
                    padding: oldPadding,
                });
                $("#" + boxId + "-corner-box").animate({
                    width: cornerWidth,
                    height: cornerHeight,
                }, 250, function() {
                    $("#" + boxId + "-expand-button").css("color", "transparent").hide();
                    $("#" + boxId).animate({
                        width: oldWidth,
                        height: oldHeight,
                    }, 250, function() {
                        $(this).resizable("enable");
                        $("#" + boxId + "-collapse-button").fadeIn(250);
                        $("#" + boxId).removeClass('collapsed'); // remove the collapsed class when the box is expanded
                        // check if the box has been expanded before
                        
                    });
                });
            });
            console.log("'"+boxId+"' has finished expanding.")
            if (!expanded) {
            }
        };
        

        return {collapseEvent, expandEvent};

    }

    updateCollapseExpandEvents() {
        console.log("is expanded: "+this.expanded);
    
        // Unbind the current collapse and expand events
        $("#" + this.boxId + "-collapse-button").off('click');
        $("#" + this.boxId + "-expand-button").off('click');
    
        // Generate the new collapse and expand events
        const {collapseEvent, expandEvent} = this.generateCollapseExpandEvents();
    
        const clickcollapse = (e) => {
            console.log("user called collapse on '"+this.boxId+"'...");
            collapseEvent(e);  // call the collapseEvent function with the event argument
        }
        
        const clickexpand = (e) => {
            console.log("user called expand on '"+this.boxId+"'...");
            expandEvent(e);  // call the expandEvent function with the event argument
        }
    
        // Bind the new collapse and expand events
        $("#" + this.boxId + "-collapse-button").on('click', clickcollapse);
        $("#" + this.boxId + "-expand-button").on('click', clickexpand);
    }  

    removeChildBox(childBoxId) {
        // Find the child box in the array
        const index = this.childBoxes.findIndex(box => box.boxId === childBoxId);

        // If the child box was found, remove it
        if (index !== -1) {
            this.childBoxes.splice(index, 1);
        }

        // Remove the HTML element
        $("#" + childBoxId).remove();
    }

    addChildBox(childBox) {
        console.log(this.boxId + " adding child "+childBox.boxId);
        childBox.parentBox = this;  // set the parent box of the child box
        this.hideChildBoxIfCollapsed(childBox);
        this.childBoxes.push(childBox);
        childBox.updateCollapseExpandEvents();
    }

    hideChildBoxIfCollapsed(childBox) {
        if ($("#" + this.boxId).hasClass('collapsed')) {
            $("#" + childBox.boxId).hide();
        }
    }

    hideChildBoxes() {
        this.childBoxes.forEach(childBox => {
            $("#" + childBox.boxId).hide();
        });
    }
}
