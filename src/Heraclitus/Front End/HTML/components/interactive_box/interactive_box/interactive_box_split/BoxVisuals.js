class BoxVisuals {
    constructor(boxId, title, mainColor, secondaryColor, tertiaryColor, parentBox = null, jsonChildren = null) {
        this.boxId = boxId;
        this.parentBox = parentBox;
        this.title = title;
        this.mainColor = mainColor;
        this.secondaryColor = secondaryColor;
        this.tertiaryColor = tertiaryColor;
        this.expanded = true;
        this.childBoxes = [];
        if (this.childBoxes.length > 0) {
            $("#" + this.boxId).addClass('collapsed');
        }
        this.jsonChildren = jsonChildren;
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

    generateHTML() {
        let minSize = this.calculateMinSize();
        let div = $('<div>', {
            id: this.boxId,
            class: 'interactive-box',
            style: `position: relative; top: 35px; width: ${minSize.minWidth}px; min-height: ${minSize.minHeight}px`
        });
        let collapseButton = $('<button>', {id: this.boxId+'-collapse-button', class: 'collapse-button', text: '-'});
        let cornerBox = $('<div>', {
            id: this.boxId+'-corner-box',
            class: 'corner-box',
            style: 'z-index: 1000;' // assign a high z-index value
        });
        let dragHandle = $('<div>', {id: this.boxId+'-drag-handle', class: 'drag-handle', style: 'width: 20px; height: 100%; position: absolute'}); 
        let cornerSpan = $('<span>', {text: this.title, style: 'margin-left: 20px;'});
        let expandButton = $('<button>', {id: this.boxId+'-expand-button', class: 'expand-button', text: '+', style: 'display: none'});
        let cornerInput = $('<input>', {type: 'text', id: this.boxId+'-corner-input', class: 'corner-input', style: 'display: none'});
        
        cornerBox.append(dragHandle, cornerSpan, expandButton);
        div.append(collapseButton, cornerBox, cornerInput);
        
        return div;
    }

    applyDynamicStyles() {
        $("#" + this.boxId).css({
            "border-color": this.mainColor,
            "background-color": this.secondaryColor
        });
        $("#" + this.boxId + "-corner-box").css({
            "border-color": this.mainColor,
            "background-color": this.mainColor,
            "text-align": "left"
        });
        $("#" + this.boxId + "-collapse-button, #" + this.boxId + "-expand-button").css({
            "color": this.tertiaryColor
        });
        $("#" + this.boxId + "-corner-input").css({
            "margin-left": "30px"
        });
        
    }

    generate(parentElement = 'body') {
        console.log("generating " + this.boxId + "'...")
        let html = this.generateHTML();
        $(parentElement).append(html);
    
        this.applyDynamicStyles();
        this.attachEvents();
    
        // Store the InteractiveBox object in the DOM element's data
        $("#" + this.boxId).data('InteractiveBox', this);
    
        // Make all boxes droppable
        $(".interactive-box").droppable();
    }
}
