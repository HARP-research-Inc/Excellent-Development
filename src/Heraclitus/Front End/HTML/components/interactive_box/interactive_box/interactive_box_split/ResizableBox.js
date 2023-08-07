class ResizableBox extends BoxVisuals {
    constructor(boxId, title, mainColor, secondaryColor, tertiaryColor, parentBox = null, jsonChildren = null) {
        super(boxId, title, mainColor, secondaryColor, tertiaryColor, parentBox, jsonChildren);
    }

    shrinkToChildBoxSize(parentId) {
        let childBoxSize = this.calculateChildBoxSize(this.boxId, this.childBoxes);
        $("#" + this.boxId).animate({
            width: childBoxSize.totalWidth,
            height: childBoxSize.totalHeight+20
        }, 250);
    }

    calculateChildBoxSize(boxId, childBoxes) {
        console.log("calculating new expanded size of '"+boxId+"' with its children");

        var totalWidth = 0;
        var totalHeight = 0;

        // Iterate over the child boxes, adding their sizes to the totals
        childBoxes.forEach(childBox => {
            console.log("In '"+boxId+"' for child: "+childBox.boxId);
            var childWidth;
            var childHeight;// = 28;

            // If the child box is expanded, use its oldWidth and oldHeight properties
            if (childBox.expanded) {
                console.log(childBox.boxId +"is currently expanded")
                // Add 20px for padding
                childWidth = childBox.oldWidth+28;
                childHeight = childBox.oldHeight+30;
            } else {
                console.log(childBox.boxId +"is NOT currently expanded")
                // If the child box is not expanded, use its current width and height
                childWidth = $("#" + childBox.boxId).outerWidth(true);
                childHeight = $("#" + childBox.boxId).outerHeight(true);
            }

            // Update totalWidth only if childWidth is greater
            totalWidth = Math.max(totalWidth, childWidth);
            totalHeight += childHeight;

            console.log("with height: "+childHeight+" the total height of '"+boxId+"' is now "+totalHeight);
        });
        self.childBoxSize = { totalWidth, totalHeight };
        return { totalWidth, totalHeight };
    }

    calculateCollapsedSize() {
        var cornerBoxWidth = $("#" + this.boxId + "-corner-box").outerWidth();
        var cornerBoxHeight = $("#" + this.boxId + "-corner-box").outerHeight();
        var collapseButtonWidth = $("#" + this.boxId + "-collapse-button").outerWidth();
        var collapsedWidth = cornerBoxWidth + collapseButtonWidth + 103;
        var collapsedHeight = cornerBoxHeight + 8;
        return { collapsedWidth, collapsedHeight };
    }

    calculateMinSize() {
        // Create invisible temporary elements with the box's title and collapse button, append them to the body, and measure their widths
        var tempSpan = $("<span>").css({display: 'inline-block', visibility: 'hidden'}).text(this.title).appendTo('body');
        var tempButton = $("<button>").css({display: 'inline-block', visibility: 'hidden'}).text('-').appendTo('body');
        var titleWidth = tempSpan.width();
        var buttonWidth = tempButton.width();
        tempSpan.remove();
        tempButton.remove();
    
        // Minimum corner box width
        var minCornerWidth = 80;
    
        // Calculate the minimum width and height
        var minWidth;
        if (minCornerWidth > (titleWidth + buttonWidth)) {
            minWidth = minCornerWidth +129
        } else {
            minWidth = titleWidth + buttonWidth + 159
        }
        return { minWidth: minWidth};
    }
}
