require('jsdom-global')();
const $ = require('jquery');
global.$ = global.jQuery = $;

class BoxBase {
    constructor(boxId, title, mainColor, secondaryColor, tertiaryColor, parentBox = null, jsonChildren = null, $ = window.$) {
        this.boxId = boxId;
        this.parentBox = parentBox;
        this.title = title;
        this.mainColor = mainColor;
        this.secondaryColor = secondaryColor;
        this.tertiaryColor = tertiaryColor;
        this.expanded = true;
        this.childBoxes = [];
        this.$ = $;
        if (this.childBoxes.length > 0) {
            $("#" + this.boxId).addClass('collapsed');
        }
        this.jsonChildren = jsonChildren;
    }

    generateHTML() {
        let div = this.$('<div>', {
            id: this.boxId,
            class: 'interactive-box'
        });
        let collapseButton = this.$('<button>', { id: this.boxId + '-collapse-button', class: 'collapse-button', text: '-' });
        let cornerBox = this.$('<div>', {
            id: this.boxId + '-corner-box',
            class: 'corner-box',
            style: 'z-index: 1000;' // assign a high z-index value
        });
        let dragHandle = this.$('<div>', { id: this.boxId + '-drag-handle', class: 'drag-handle', style: 'width: 20px; height: 100%; position: absolute' });
        let cornerSpan = this.$('<span>', { text: this.title, style: 'margin-left: 20px;' });
        let expandButton = this.$('<button>', { id: this.boxId + '-expand-button', class: 'expand-button', text: '+', style: 'display: none' });
        let cornerInput = this.$('<input>', { type: 'text', id: this.boxId + '-corner-input', class: 'corner-input', style: 'display: none' });

        cornerBox.append(dragHandle, cornerSpan, expandButton);
        div.append(collapseButton, cornerBox, cornerInput);

        return div;
    }

    toDOMElement() {
        if (!this.domElement) {
            this.domElement = document.createElement('div');
            this.domElement.id = this.id;
            this.domElement.boxId = this.boxId;
            this.domElement.title = this.title;
            this.domElement.mainColor = this.mainColor;
            this.domElement.secondaryColor = this.secondaryColor;
            this.domElement.tertiaryColor = this.tertiaryColor;
            this.domElement.parentBox = this.parentBox;
            this.domElement.jsonChildren = this.jsonChildren;
            this.domElement.$ = this.$;
            // ...add other properties and children as necessary...
        }
        return this.domElement;
    }


    applyDynamicStyles() {
        this.$("#" + this.boxId).css({
            "border-color": this.mainColor,
            "background-color": this.secondaryColor
        });
        this.$("#" + this.boxId + "-corner-box").css({
            "border-color": this.mainColor,
            "background-color": this.mainColor,
            "text-align": "left"
        });
        this.$("#" + this.boxId + "-collapse-button, #" + this.boxId + "-expand-button").css({
            "color": this.tertiaryColor
        });
        this.$("#" + this.boxId + "-corner-input").css({
            "margin-left": "30px"
        });

    }

    commonGenerate() {
        console.log("generating " + this.boxId + "'...")
        let html = this.generateHTML();

        // Store the InteractiveBox object in the DOM element's data
        $("#" + this.boxId).data('InteractiveBox', this);
    }

    generate(parentElement = 'body') {
        this.commonGenerate();
    }
}

class ResizableBox extends BoxBase {
    constructor(boxId, title, mainColor, secondaryColor, tertiaryColor, parentBox = null, jsonChildren = null, $ = window.$) {
        super(boxId, title, mainColor, secondaryColor, tertiaryColor, parentBox, jsonChildren);
        this.$ = $;
        this.domElement = null; // new property
    }

    generateHTML() {
        let minSize = this.calculateMinSize();
        let div = super.generateHTML();
        div.css({
            position: 'relative',
            top: '35px',
            width: `${minSize.minWidth}px`,
            minHeight: `${minSize.minHeight}px`
        });
        return div;
    }

    toDOMElement() {
        if (!this.domElement) {
            this.domElement = document.createElement('div');
            this.domElement.id = this.id;
            this.domElement.boxId = this.boxId;
            this.domElement.title = this.title;
            this.domElement.mainColor = this.mainColor;
            this.domElement.secondaryColor = this.secondaryColor;
            this.domElement.tertiaryColor = this.tertiaryColor;
            this.domElement.parentBox = this.parentBox;
            this.domElement.jsonChildren = this.jsonChildren;
            this.domElement.$ = this.$;
            // ...add other properties and children as necessary...
        }
        return this.domElement;
    }

    shrinkToChildBoxSize(parentId) {
        let childBoxSize = this.calculateChildBoxSize(this.boxId, this.childBoxes);
        this.$("#" + this.boxId).animate({
            width: childBoxSize.totalWidth,
            height: childBoxSize.totalHeight + 20
        }, 250);
    }

    calculateChildBoxSize(boxId, childBoxes) {
        console.log("calculating new expanded size of '" + boxId + "' with its children");

        var totalWidth = 0;
        var totalHeight = 0;

        // Iterate over the child boxes, adding their sizes to the totals
        childBoxes.forEach(childBox => {
            console.log("In '" + boxId + "' for child: " + childBox.boxId);
            var childWidth;
            var childHeight;// = 28;

            // If the child box is expanded, use its oldWidth and oldHeight properties
            if (childBox.expanded) {
                console.log(childBox.boxId + "is currently expanded")
                // Add 20px for padding
                childWidth = childBox.oldWidth + 28;
                childHeight = childBox.oldHeight + 30;
            } else {
                console.log(childBox.boxId + "is NOT currently expanded")
                // If the child box is not expanded, use its current width and height
                childWidth = this.$("#" + childBox.boxId).outerWidth(true);
                childHeight = this.$("#" + childBox.boxId).outerHeight(true);
            }

            // Update totalWidth only if childWidth is greater
            totalWidth = Math.max(totalWidth, childWidth);
            totalHeight += childHeight;

            console.log("with height: " + childHeight + " the total height of '" + boxId + "' is now " + totalHeight);
        });
        self.childBoxSize = { totalWidth, totalHeight };
        return { totalWidth, totalHeight };
    }

    calculateCollapsedSize() {
        var cornerBoxWidth = this.$("#" + this.boxId + "-corner-box").outerWidth();
        console.log('cornerBoxWidth:', cornerBoxWidth);
        var cornerBoxHeight = this.$("#" + this.boxId + "-corner-box").outerHeight();
        console.log('cornerBoxHeight:', cornerBoxHeight);
        var collapseButtonWidth = this.$("#" + this.boxId + "-collapse-button").outerWidth();
        console.log('collapseButtonWidth:', collapseButtonWidth);
        var collapsedWidth = cornerBoxWidth + collapseButtonWidth + 103;
        var collapsedHeight = cornerBoxHeight + 8;
        return { collapsedWidth, collapsedHeight };
    }    

    calculateMinSize() {
        // Create invisible temporary elements with the box's title and collapse button, append them to the body, and measure their widths
        var tempSpan = this.$("<span>").css({ display: 'inline-block', visibility: 'hidden' }).text(this.title).appendTo('body');
        var tempButton = this.$("<button>").css({ display: 'inline-block', visibility: 'hidden' }).text('-').appendTo('body');
        var titleWidth = tempSpan.width();
        var buttonWidth = tempButton.width();
        tempSpan.remove();
        tempButton.remove();

        // Minimum corner box width
        var minCornerWidth = 80;

        // Calculate the minimum width and height
        var minWidth;
        if (minCornerWidth > (titleWidth + buttonWidth)) {
            minWidth = minCornerWidth + 129
        } else {
            minWidth = titleWidth + buttonWidth + 159
        }
        return { minWidth: minWidth };
    }
}

class EventBox extends ResizableBox {
    constructor(boxId, title, mainColor, secondaryColor, tertiaryColor, parentBox = null, jsonChildren = null, $ = window.$) {
        super(boxId, title, mainColor, secondaryColor, tertiaryColor, parentBox, jsonChildren, $);
    }

    attachEvents() {
        super.attachEvents();
        var box = this;
        var parentId = this.parentBox;
        var oldWidth = this.$("#" + this.boxId).width();
        var oldHeight = this.$("#" + this.boxId).height();
        var oldPadding = this.$("#" + this.boxId).css('padding');
        var cornerWidth = this.$("#" + this.boxId + "-corner-box").outerWidth();
        var cornerHeight = this.$("#" + this.boxId + "-corner-box").outerHeight();
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
            resize: function (event, ui) {
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
            accept: function (draggable) {
                // Only accept draggable if this box is expanded or the draggable is the background
                return $(this).hasClass('expanded') || draggable.attr('id') === 'background';
            },
            drop: function (event, ui) {
                var dropped = ui.helper;
                var droppedOn = this.$(this);
                if (droppedOn.hasClass('collapsed')) {
                    // If the box is collapsed, find the box beneath it and drop on that instead
                    var beneathBox = droppedOn.parent().closest('.interactive-box');
                    if (beneathBox.length > 0) {
                        droppedOn = beneathBox;
                    }
                }
                if (droppedOn.attr('id') === 'body') { //if (droppedOn.attr('id') === 'edit_plane') {
                    $(dropped).detach().css({ top: 0, left: 0 }).appendTo(droppedOn);
                    $(dropped).removeChildBox().css({ top: 0, left: 0 });
                } else {
                    $(dropped).detach().css({ top: 0, left: 0 }).appendTo(droppedOn);
                    $(dropped).addChildBox(droppedOn);
                    $(dropped).removeChildBox().css({ top: 0, left: 0 });
                }
            }
        });

        $("#" + boxId).draggable({
            handle: "#" + boxId + "-corner-box" + " .drag-handle",
            helper: "clone",
            appendTo: 'body',
            start: function () {
                $(this).css({
                    'opacity': '0.2'
                });
                // Temporarily disable droppable functionality for this item
                $(this).droppable('disable');
            },
            stop: function (event, ui) {
                $(this).css({ 'opacity': '1' });

                // Temporarily hide the draggable element
                $(this).hide();

                // Now when you call elementFromPoint, it will return the underlying element
                var droppedOn = this.$(document.elementFromPoint(event.clientX, event.clientY));

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
                    $(this).detach().css({ top: 0, left: 0 }).appendTo('body');
                } else if (droppedOn.hasClass('interactive-box')) {
                    console.log("Dropped on another interactive box: " + droppedOn[0].boxId); //WORK ON MEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
                    $(this).detach().css({ top: 0, left: 0 }).appendTo(droppedOn);
                }
            }

        }).resizable();


        $("#" + boxId).click(function () {
            // Bring the clicked box to the front by setting its z-index to the maximum z-index plus one
            var maxZ = Math.max.apply(null, $.map($('body > *'), function (e, n) {
                if ($(e).css('position') != 'static')
                    return parseInt($(e).css('z-index')) || 1;
            }));
            $(this).css('z-index', maxZ + 1);
        });

        setMinSize();

        $("#" + boxId + "-corner-box span").on('click', function () {
            var width = this.$(this).parent().outerWidth() - 20;  // reduce the width by the width of the drag handle
            var height = this.$(this).parent().outerHeight();
            $(this).parent().hide();
            $("#" + boxId + "-corner-input").css({ width: width, height: height }).val($(this).text().trim()).show().focus();
            setMinSize();
        });


        $("#" + boxId + "-corner-input").on('focusout', function () {
            let newTitle = this.$(this).val();
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

        $("#" + boxId + "-corner-input").on('keyup', function (e) {
            if (e.key === 'Enter' || e.keyCode === 13) {
                $(this).trigger('focusout');
            }
        });

        this.updateCollapseExpandEvents();  // Use the new method here

        $("#" + this.boxId + "-collapse-button").click();  // trigger the initial collapse
    }

    childBoxExpanded(childBox) {
        // Recalculate oldWidth and oldHeight based on the expanded child box
        console.log("'" + childBox.boxId + "' called size update for '" + this.boxId + "'");

        // Generate the new collapse and expand events
        const { collapseEvent, expandEvent } = this.generateCollapseExpandEvents();
        if (childBox.parentBox != null) {
            $("#" + this.boxId + "-expand-button").click();  // trigger a click event on the expand button
        }
    }

    childBoxShrunk(childBox) {
        console.log("'" + childBox.boxId + "' called size update for '" + this.boxId + "'");

        // Generate the new collapse and expand events
        const { collapseEvent, expandEvent } = this.generateCollapseExpandEvents();
        if (childBox.parentBox != null) {
            //$("#" + this.boxId + "-expand-button").click();  // trigger a click event on the collapse button
        }
    }

    generateCollapseExpandEvents() {
        var box = this;
        var expanded = this.expanded;
        var oldWidth = this.$("#" + this.boxId).width();
        var oldHeight = this.$("#" + this.boxId).height();
        var oldPadding = this.$("#" + this.boxId).css('padding');
        var cornerWidth = this.$("#" + this.boxId + "-corner-box").outerWidth();
        var cornerHeight = this.$("#" + this.boxId + "-corner-box").outerHeight();
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
                    $(this).fadeOut(250, function () {
                        $("#" + boxId + "-corner-box").animate({
                            width: minWidth,
                            height: minHeight,
                        }, 250, function () {
                            $("#" + boxId + "-expand-button").css("color", tertiaryColor).show();
                            $("#" + boxId).animate({
                                width: minWidth,
                                height: minHeight,
                            }, 250, function () {
                                $(this).css({
                                    padding: 0,
                                }).resizable("disable");
                                $("#" + boxId + " > .interactive-box").hide();  // hide only direct child boxes
                                if (parentBox != null) {
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
                    oldHeight = Math.max(oldHeight, childBoxSize.totalHeight + 20);
                };
                this.oldWidth = oldWidth;
                this.oldHeight = oldHeight;
                expanded = true;
                this.expanded = expanded; // Update the expanded property
                if (parentBox != null) {
                    parentBox.childBoxExpanded(thisBox)
                }
                // If this is the first time the box is being expanded and it has JSON children, parse them
                // If this is the first time the box is being expanded and it has JSON children, parse them
                if (!this.expanded && this.jsonChildren) {
                    console.error("Dependancy Issue! WIP fix JSON")
                    this.parseJsonToInteractiveBoxes(this.jsonChildren);
                    this.jsonChildren = null;  // Clear the JSON children to prevent them from being parsed again
                }

                console.log("'" + this.boxId + "' has oldHeight " + oldHeight);
                $("#" + boxId).css({
                    padding: oldPadding,
                });
                $("#" + boxId + "-corner-box").animate({
                    width: cornerWidth,
                    height: cornerHeight,
                }, 250, function () {
                    $("#" + boxId + "-expand-button").css("color", "transparent").hide();
                    $("#" + boxId).animate({
                        width: oldWidth,
                        height: oldHeight,
                    }, 250, function () {
                        $(this).resizable("enable");
                        $("#" + boxId + "-collapse-button").fadeIn(250);
                        $("#" + boxId).removeClass('collapsed'); // remove the collapsed class when the box is expanded
                        // check if the box has been expanded before

                    });
                });
            });
            console.log("'" + boxId + "' has finished expanding.")
            if (!expanded) {
            }
        };


        return { collapseEvent, expandEvent };

    }

    updateCollapseExpandEvents() {
        console.log("is expanded: " + this.expanded);
        if (document) {
            // Unbind the current collapse and expand events
            $("#" + this.boxId + "-collapse-button").off('click');
            $("#" + this.boxId + "-expand-button").off('click');

            // Generate the new collapse and expand events
            const { collapseEvent, expandEvent } = this.generateCollapseExpandEvents();

            const clickcollapse = (e) => {
                console.log("user called collapse on '" + this.boxId + "'...");
                collapseEvent(e);  // call the collapseEvent function with the event argument
            }

            const clickexpand = (e) => {
                console.log("user called expand on '" + this.boxId + "'...");
                expandEvent(e);  // call the expandEvent function with the event argument
            }

            // Bind the new collapse and expand events
            $("#" + this.boxId + "-collapse-button").on('click', clickcollapse);
            $("#" + this.boxId + "-expand-button").on('click', clickexpand);
        } else {
            console.error("No Document!");
        }
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
        console.log(this.boxId + " adding child " + childBox.boxId);
        childBox.parentBox = this;  // set the parent box of the child box
        if (childBox && childBox.boxId) {
            this.hideChildBoxIfCollapsed(childBox);
            childBox.updateCollapseExpandEvents();
        }
        this.childBoxes.push(childBox);
    }

    hideChildBoxIfCollapsed(childBox) {
        if (document) {
            if (this && this.boxId) {
                if (childBox && childBox.boxId) {
                    if (childBox && childBox.boxId && $("#" + this.boxId).hasClass('collapsed')) {
                        $("#" + childBox.boxId).hide();
                    }
                } else {
                    console.warn("Warning: The child object or its boxId is not defined.");
                }
            } else {
                console.warn("Warning: The calling object or its boxId is not defined.");
            }
        } else {
            console.error("No document!")
        }
    }

    hideChildBoxes() {
        this.childBoxes.forEach(childBox => {
            $("#" + childBox.boxId).hide();
        });
    }
}

class InteractiveBox extends EventBox {
    constructor(boxId, title, mainColor, secondaryColor, tertiaryColor, parentBox = null, jsonChildren = null, $ = window.$) {
            super(boxId, title, mainColor, secondaryColor, tertiaryColor, parentBox, jsonChildren, $);
    }

    generateChildBoxes(boxId, childBoxes) {
        console.log("'" + boxId + "' is generating children...");
        // Iterate over the child boxes array and generate each one
        childBoxes.forEach(childBox => {
            // Check if the child box is already present in the parent
            if ($("#" + childBox.boxId).length === 0) {
                // If not, generate the child box
                console.log("'" + childBox.boxId + "' generated");
                childBox.generate('#' + boxId);
            } else {
                console.log("'" + childBox.boxId + "' already present in the parent");
            }
        });
    }

    generate(parentElement = 'body') {
        super.commonGenerate();
        
        let html = this.generateHTML();
        $(parentElement).append(html);

        this.applyDynamicStyles();

        // parse JSON data to InteractiveBoxes
        this.parseJsonToInteractiveBoxes(this.jsonChildren);

        // Make all boxes droppable
        $(".interactive-box").droppable();
    }

    parseJsonToInteractiveBoxes(jsonObject) {
        let box = null;

        if (Array.isArray(jsonObject)) {
            // If it's a list, create boxes with the values as titles and no children
            for (let title of jsonObject) {
                box = new InteractiveBox('box' + boxIdCounter++, title, this.mainColor, this.secondaryColor, this.tertiaryColor, this);
                this.addChildBox(box);
            }
        } else {
            // If it's an object, the keys are the titles and the values are the children
            var boxIdCounter = 0;
            for (let title in jsonObject) {
                let children = jsonObject[title];
                if (children && typeof children === "object") {
                    // Instead of creating child boxes, pass the JSON to the children
                    box = new InteractiveBox('box' + boxIdCounter++, title, this.mainColor, this.secondaryColor, this.tertiaryColor, this, children);
                    this.addChildBox(box);
                } else {
                    box = new InteractiveBox('box' + boxIdCounter++, title, this.mainColor, this.secondaryColor, this.tertiaryColor, this);
                    this.addChildBox(box);
                }
            }
        }
    }

}

module.exports = { InteractiveBox, BoxBase, EventBox, ResizableBox };