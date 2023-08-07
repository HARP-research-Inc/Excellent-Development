class InteractiveBox {
    constructor(boxId, title, mainColor, secondaryColor) {
        this.boxId = boxId;
        this.title = title;
        this.mainColor = mainColor;
        this.secondaryColor = secondaryColor;
    }

    generateHTML() {
        return `
        <div id="${this.boxId}" style="background-color:${this.mainColor};border-color:${this.secondaryColor};">
            <button id="${this.boxId}-collapse-button" style="color:${this.secondaryColor};">-</button>
            <div id="${this.boxId}-corner-box" style="background-color:${this.secondaryColor};border-color:${this.mainColor};color:${this.mainColor};">
                <span>${this.title}</span>
                <button id="${this.boxId}-expand-button" style="display: none;color:${this.secondaryColor};">+</button>
            </div>
            <input type="text" id="${this.boxId}-corner-input" style="display: none;">
        </div>
        `;
    }

    generateCSS() {
        return `
        #${this.boxId} {
            width: 235px;
            height: 200px;
            border: 2px solid ${this.mainColor};
            border-radius: 2px;
            position: relative;
        }
        
        #${this.boxId}-corner-box {
            min-width: 80px;
            min-height: 30px;
            background-color: #FF7E7E;
            position: absolute;
            top: 0;
            left: 0;
            cursor: pointer;
            border-radius: 2px;
            color: #000;
            border: 2px solid #FF7E7E;
            border-radius: 2px;
            padding: 5px 15px 5px 5px;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 1.1em;
        }
        
        #${this.boxId}-corner-box span {
            display: inline-block;
            vertical-align: middle;
            white-space: nowrap;  /* prevents text from wrapping to new line */
        }
        
        #${this.boxId}-corner-input {
            position: absolute;
            top: 0;
            left: 0;
            border: none;
            padding: 0;
            margin: 0;
            text-align: center;
            box-sizing: border-box;
            font-size: 1.1em;
            width: 70px;  /* fixed width to match corner box */
            height: 35px;  /* fixed height to match corner box */
        }
        
        #${this.boxId}-collapse-button, #${this.boxId}-expand-button {
            padding: 5px 15px 5px 5px;
            background: transparent;
            color: #A95454;
            border: none;
            cursor: pointer;
            font-size: 1.5em;
        }
        
        #${this.boxId}-collapse-button {
            position: absolute;
            top: 0;
            right: 0;
        }
        
        #${this.boxId}-expand-button {
            margin-left: 115px;
            margin-right: -15px;
            vertical-align: middle;
        }
        `
    }

    generateJS() {
        return `
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
        `;
    }

    generate() {
        let html = this.generateHTML();
        $('body').append(html);
    
        let css = this.generateCSS();
        $('head').append(`<style>${css}</style>`);
    
        let js = this.generateJS();
        let script = document.createElement('script');
        script.textContent = js;
        document.body.appendChild(script);
    }    
}

// Now you can create instances of InteractiveBox:
let box1 = new InteractiveBox('box1', 'Box 1', '#FFF3F3', '#FF7E7E');
box1.generate();
let box2 = new InteractiveBox('box2', 'Box 2', '#F3FFFF', '#7E7EFF');
box2.generate();
// ... and so on
