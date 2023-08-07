const { JSDOM } = require("jsdom");
const jQuery = require("jquery");
require('jsdom-global')();

let $;
let window;
let document;
let navigator;

beforeAll(async () => {
    const dom = await JSDOM.fromFile("index.html", {});
    window = dom.window;
    document = window.document;
    navigator = window.navigator;
    $ = jQuery(window);

    // Add jQuery, document, window, and navigator to the global scope
    global.jQuery = $;
    global.document = document;
    global.window = window;
    global.navigator = navigator;

    global.$ = $;
    require("jquery-ui-dist/jquery-ui");
    require("jquery-ui/ui/widgets/mouse");
    require("jquery-ui/ui/widgets/sortable");
});

describe('DOM environment tests', () => {
    test('window object exists', () => {
        expect(window).toBeDefined();
    });

    test('document object exists', () => {
        expect(document).toBeDefined();
    });

    test('navigator object exists', () => {
        expect(navigator).toBeDefined();
    });

    test('jQuery is correctly loaded', () => {
        expect($).toBeDefined();
        expect($.fn.jquery).toMatch(/(\d+\.)?(\d+\.)?(\d+\.)?(\d+)/); // Check if jQuery version can be determined
    });

    test('jQuery UI is correctly loaded', () => {
        expect($.ui).toBeDefined();
        expect($.ui.version).toMatch(/(\d+\.)?(\d+\.)?(\d+\.)?(\d+)/); // Check if jQuery UI version can be determined
    });

    test('jQuery UI sortable is available', () => {
        const sortableElement = $('<div>').appendTo('body');
        sortableElement.sortable();
        expect(sortableElement.sortable('instance')).toBeDefined();
        sortableElement.remove();
    });

    test('jQuery UI resizable is available', () => {
        const resizableElement = $('<div>').appendTo('body');
        resizableElement.resizable();
        expect(resizableElement.resizable('instance')).toBeDefined();
        resizableElement.remove();
    });

    test('jQuery UI draggable is available', () => {
        const draggableElement = $('<div>').appendTo('body');
        draggableElement.draggable();
        expect(draggableElement.draggable('instance')).toBeDefined();
        draggableElement.remove();
    });

    // Add more tests for specific DOM features as needed
});

describe('DOM modification tests', () => {
    class DomModifier {
        constructor(document) {
            this.document = document;
        }

        addDivToBody() {
            let div = this.document.createElement('div');
            this.document.body.appendChild(div);
        }

        changeElementText(id, newText) {
            let element = this.document.getElementById(id);
            if (element) {
                element.textContent = newText;
            }
        }

        removeElement(id) {
            const element = document.getElementById(id);
            if (element) {
                element.parentNode.removeChild(element);
            }
        }        

        addClassToElement(id, className) {
            let element = this.document.getElementById(id);
            if (element) {
                element.classList.add(className);
            }
        }
    }

    beforeAll(() => {
        dom = new JSDOM('<!doctype html><html><body></body></html>');
        window = dom.window;
        document = window.document;
        domModifier = new DomModifier(document);
    });

    beforeEach(() => {
        let testDiv = document.createElement('div');
        testDiv.id = 'testDiv';
        document.body.appendChild(testDiv);
    });

    afterEach(() => {
        testDiv = document.getElementById('testDiv');
        if (testDiv != null){
            domModifier.removeElement('testDiv');
        }
    });

    test('adds div to body', () => {
        domModifier.addDivToBody();
        const divs = document.getElementsByTagName('div');
        expect(divs.length).toBe(2);
    });

    test('changes element text', () => {
        domModifier.changeElementText('testDiv', 'New Text');
        const testDiv = document.getElementById('testDiv');
        expect(testDiv.textContent).toBe('New Text');
    });

    test('removes element', (done) => {
        domModifier.addDivToBody();
        setTimeout(() => {
            domModifier.removeElement('testDiv');
            const testDiv = document.getElementById('testDiv');
            expect(testDiv).toBeNull();
            done();
        }, 1000);  // Delay by 1 second
    });

    test('adds class to element', () => {
        domModifier.addDivToBody();
        domModifier.addClassToElement('testDiv', 'newClass');
        const testDiv = document.getElementById('testDiv');
        expect(testDiv.classList.contains('newClass')).toBe(true);
    });

    // Add more tests as needed
});

describe('DOM Querying Tests', () => {
    beforeAll(() => {
        // Adding an element to the DOM
        dom = new JSDOM('<!doctype html><html><body></body></html>');
        window = dom.window;
        document = window.document;
    });

    beforeEach(() => {
        // Adding an element to the DOM using jQuery
        $('<div/>', {
            id: 'testElement',
        }).appendTo('body');
        // Update JSDOM's representation of the document
        dom = new JSDOM($('body').html());
        document = dom.window.document;
    });

    afterEach(() => {
        testDiv = document.getElementById('testElement');
        if (testDiv != null){
            domModifier.removeElement('testElement');
        }
    });

    test('Element exists in the document', () => {
        const element = document.getElementById('testElement');
        expect(element).not.toBeNull();
    });

    test('jQuery can select the element', () => {
        const jQueryElement = $('#testElement');
        expect(jQueryElement.length).toBe(1);
    });
});

describe('BoxBase', () => {
    let boxBase;
    const { BoxBase } = require('./../InteractiveBox');

    beforeAll((done) => {
        JSDOM.fromFile("index.html", {}).then(dom => {
            window = dom.window;
            document = window.document;
            navigator = window.navigator;
            $ = jQuery(window);
    
            // Add jQuery, document, window, and navigator to the global scope
            global.jQuery = $;
            global.document = document;
            global.window = window;
            global.navigator = navigator;
    
            global.$ = $;
            require("jquery-ui-dist/jquery-ui");
            require("jquery-ui/ui/widgets/mouse");
            require("jquery-ui/ui/widgets/sortable");
    
            // Explicitly set the HTML of the body element
            $('body').html('<div id="test-element"></div>');
    
            done();
        });
    }); 

    beforeEach(() => {
        boxBase = new BoxBase('box1', 'Title', '#000', '#fff', '#f00', null, null, $);
        $(boxBase.generateHTML()).appendTo('body');
        // Update JSDOM's representation of the document
        window.document.documentElement.innerHTML = $('body').html();
    });

    afterEach(() => {
        // Remove all child elements from the body after each test
        while (document.body.firstChild) {
            document.body.firstChild.remove();
        }
    });

    test('BoxBase instance is created correctly', () => {
        expect(boxBase).toBeInstanceOf(BoxBase);
        expect(boxBase.boxId).toBe('box1');
        expect(boxBase.title).toBe('Title');
        expect(boxBase.mainColor).toBe('#000');
        expect(boxBase.secondaryColor).toBe('#fff');
        expect(boxBase.tertiaryColor).toBe('#f00');
    });

    test('generateHTML returns correct HTML structure', () => {
        const html = boxBase.generateHTML();
        expect(html.prop('id')).toBe('box1');
        expect(html.hasClass('interactive-box')).toBe(true);
        expect(html.find('.collapse-button').length).toBe(1);
        expect(html.find('.corner-box').length).toBe(1);
        expect(html.find('.drag-handle').length).toBe(1);
        expect(html.find('.expand-button').length).toBe(1);
        expect(html.find('.corner-input').length).toBe(1);
    });

    test('applyDynamicStyles applies correct styles', () => {
        boxBase.applyDynamicStyles();
        expect($('#box1').css('border-color')).toBe('#000');
        expect($('#box1').css('background-color')).toBe('rgb(255, 255, 255)');
        expect($('#box1-corner-box').css('border-color')).toBe('#000');
        expect($('#box1-corner-box').css('background-color')).toBe('rgb(0, 0, 0)');
        expect($('#box1-corner-box').css('text-align')).toBe('left');
        expect($('#box1-collapse-button, #box1-expand-button').css('color')).toBe('rgb(255, 0, 0)');
        expect($('#box1-corner-input').css('margin-left')).toBe('30px');
    });
});


describe('ResizableBox', () => {
    let resizableBox;
    const { ResizableBox } = require('./../InteractiveBox');

    beforeAll((done) => {
        JSDOM.fromFile("index.html", {}).then(dom => {
            window = dom.window;
            document = window.document;
            navigator = window.navigator;
            $ = jQuery(window);
    
            // Add jQuery, document, window, and navigator to the global scope
            global.jQuery = $;
            global.document = document;
            global.window = window;
            global.navigator = navigator;
    
            global.$ = $;
            require("jquery-ui-dist/jquery-ui");
            require("jquery-ui/ui/widgets/mouse");
            require("jquery-ui/ui/widgets/sortable");
    
            // Explicitly set the HTML of the body element
            $('body').html('<div id="test-element"></div>');
    
            done();
        });
    });    

    beforeEach(() => {
        resizableBox = new ResizableBox('box1', 'Title', '#000', '#fff', '#f00', null, null, $);
        $(resizableBox.toDOMElement()).appendTo('body');
        // Log the innerHTML before the update
        ////console.log("'document' HTML: \n"+window.document.documentElement.innerHTML);
        // Update JSDOM's representation of the document
        window.document.documentElement.innerHTML = $('body').html();
        // Log the innerHTML after the update
        ////console.log("Updating JSDOM representation... new 'document' HTML: \n"+window.document.documentElement.innerHTML);
    });
    
    afterEach(() => {
        // Remove all child elements from the body after each test
        ////console.log("Removing all children elements from body: \n")
        while (document.body.firstChild) {
            ////console.log("Removing: \n"+document.body.firstChild);
            document.body.firstChild.remove();
        }
        ////console.log("Updated 'document' HTML: \n"+window.document.documentElement.innerHTML);
    });

    test('constructs properly', () => {
        expect(resizableBox.boxId).toBe('box1');
        expect(resizableBox.title).toBe('Title');
        expect(resizableBox.mainColor).toBe('#000');
        expect(resizableBox.secondaryColor).toBe('#fff');
        expect(resizableBox.tertiaryColor).toBe('#f00');
        expect(resizableBox.expanded).toBeTruthy();
        expect(resizableBox.childBoxes).toEqual([]);
        expect(resizableBox.jsonChildren).toBeNull();
    });

    describe('JQuery', () => {

        test('jQuery can select an element', async () => {
            // Add the test-element to the body
            const testElement = document.createElement('div');
            testElement.id = 'test-element';
            document.body.appendChild(testElement);
        
            // Update JSDOM's representation of the document
            window.document.documentElement.innerHTML = $('body').html();
        
            // Try to select the test-element with the native method
            const selectedElement = document.getElementById('test-element');
        
            // Check that the native method was able to select the element
            expect(selectedElement).not.toBeNull();
        });
        
        test('jQuery can select an element by id', () => {
            // Add the test-element to the body
            const testElement = document.createElement('div');
            testElement.id = 'test-element';
            document.body.appendChild(testElement);
        
            // Update JSDOM's representation of the document
            window.document.documentElement.innerHTML = $('body').html();
        
            // Try to select the test-element with jQuery
            const selectedElement = $('#test-element');
        
            // Check that jQuery was able to select the element
            expect(selectedElement.length).toBe(1);
        });
        
        test('jQuery can append an element to the body', () => {
            // Create a new element with jQuery
            const newElement = $('<div id="new-element"></div>');
        
            // Append the new element to the body
            $('body').append(newElement);
        
            // Update JSDOM's representation of the document
            window.document.documentElement.innerHTML = $('body').html();
        
            // Try to select the new element with the native method
            const selectedElement = document.getElementById('new-element');
        
            // Check that the new element was added to the body
            expect(selectedElement).not.toBeNull();
        });
        
        test('jQuery can remove an element from the body', () => {
            // Add the test-element to the body
            const testElement = document.createElement('div');
            testElement.id = 'test-element';
            document.body.appendChild(testElement);
        
            // Update JSDOM's representation of the document
            window.document.documentElement.innerHTML = $('body').html();
        
            // Remove the test-element with jQuery
            $('#test-element').remove();
        
            // Update JSDOM's representation of the document
            window.document.documentElement.innerHTML = $('body').html();
        
            // Try to select the test-element with the native method
            const selectedElement = document.getElementById('test-element');
        
            // Check that the test-element was removed from the body
            expect(selectedElement).toBeNull();
        });

        test('jQuery is available within class methods', () => {
            class TestClass {
                constructor() {
                    this.element = $('<div id="class-element"></div>');
                }
        
                appendElementToBody() {
                    $('body').append(this.element);
                }
        
                removeElementFromBody() {
                    $('#class-element').remove();
                }
            }
        
            const testClass = new TestClass();
        
            // Append the element to the body
            testClass.appendElementToBody();
        
            // Update JSDOM's representation of the document
            window.document.documentElement.innerHTML = $('body').html();
        
            // Try to select the element with the native method
            let selectedElement = document.getElementById('class-element');
        
            // Check that the element was added to the body
            expect(selectedElement).not.toBeNull();
        
            // Remove the element from the body
            testClass.removeElementFromBody();
        
            // Update JSDOM's representation of the document
            window.document.documentElement.innerHTML = $('body').html();
        
            // Try to select the element with the native method
            selectedElement = document.getElementById('class-element');
        
            // Check that the element was removed from the body
            expect(selectedElement).toBeNull();
        }); 

        test('jQuery is available WITH PASS IN within external class methods', () => {
            // Import the external class
            const { ExternalClassDolla }  = require('./ExternalClass');
            const externalClass = new ExternalClassDolla($);

            // Append the element to the body
            externalClass.appendElementToBody();

            // Update JSDOM's representation of the document
            window.document.documentElement.innerHTML = $('body').html();

            // Try to select the element with the native method
            let selectedElement = document.getElementById('class-element');

            // Check that the element was added to the body
            expect(selectedElement).not.toBeNull();

            // Remove the element from the body
            externalClass.removeElementFromBody();

            // Update JSDOM's representation of the document
            window.document.documentElement.innerHTML = $('body').html();

            // Try to select the element with the native method
            selectedElement = document.getElementById('class-element');

            // Check that the element was removed from the body
            expect(selectedElement).toBeNull();
        });

    });
    
    test('calculates minimum size correctly', () => {
        // Set up a DOM element for the test
        const element = document.createElement('div');
        element.id = resizableBox.boxId + '-corner-box';
        document.body.appendChild(element);
    
        // Run the method
        const minSize = resizableBox.calculateMinSize();
    
        // Assert that minWidth is correctly calculated based on your logic
        expect(minSize.minWidth).toBeGreaterThan(0);
    });

    test('calculates collapsed size correctly', () => {
        // You need to append some elements to the DOM here
        const collapsedSize = resizableBox.calculateCollapsedSize();
        // Assert that collapsedWidth and collapsedHeight are correctly calculated
        expect(collapsedSize.collapsedWidth).toBeGreaterThan(0);
        expect(collapsedSize.collapsedHeight).toBeGreaterThan(0);
    });

    test('calculates child box size correctly', () => {
        const childBoxSize = resizableBox.calculateChildBoxSize(resizableBox.boxId, resizableBox.childBoxes);
        // Assert that totalWidth and totalHeight are correctly calculated
        expect(childBoxSize.totalWidth).toBe(0);
        expect(childBoxSize.totalHeight).toBe(0);
    });

    test('shrinks to child box size correctly', () => {
        resizableBox.shrinkToChildBoxSize(resizableBox.boxId);
        // You need to add assertions here to check the size of the resizableBox element
    });
});

describe.skip("InteractiveBox", () => {
    let box;
    const { InteractiveBox } = require('./../InteractiveBox');

    beforeAll((done) => {
        JSDOM.fromFile("index.html", {}).then(dom => {
            window = dom.window;
            document = window.document;
            navigator = window.navigator;
            $ = jQuery(window);
    
            // Add jQuery, document, window, and navigator to the global scope
            global.jQuery = $;
            global.document = document;
            global.window = window;
            global.navigator = navigator;
    
            global.$ = $;
            require("jquery-ui-dist/jquery-ui");
            require("jquery-ui/ui/widgets/mouse");
            require("jquery-ui/ui/widgets/sortable");
    
            // Explicitly set the HTML of the body element
            $('body').html('<div id="test-element"></div>');
    
            done();
        });
    });    

    beforeEach(() => {
        resizableBox = new InteractiveBox('box1', 'Title', '#000', '#fff', '#f00', null, null, $);
        $(resizableBox.toDOMElement()).appendTo('body');
        // Log the innerHTML before the update
        ////console.log("'document' HTML: \n"+window.document.documentElement.innerHTML);
        // Update JSDOM's representation of the document
        window.document.documentElement.innerHTML = $('body').html();
        // Log the innerHTML after the update
        ////console.log("Updating JSDOM representation... new 'document' HTML: \n"+window.document.documentElement.innerHTML);
    });
    
    afterEach(() => {
        // Remove all child elements from the body after each test
        ////console.log("Removing all children elements from body: \n")
        while (document.body.firstChild) {
            ////console.log("Removing: \n"+document.body.firstChild);
            document.body.firstChild.remove();
        }
        ////console.log("Updated 'document' HTML: \n"+window.document.documentElement.innerHTML);
    });

    test('constructs properly', () => {
        expect(box.boxId).toBe('box1');
        expect(box.title).toBe('Title');
        expect(box.mainColor).toBe('#000');
        expect(box.secondaryColor).toBe('#fff');
        expect(box.tertiaryColor).toBe('#f00');
        expect(box.expanded).toBeTruthy();
        expect(box.childBoxes).toEqual([]);
        expect(box.jsonChildren).toBeNull();
    });

    test('parses JSON to interactive boxes correctly', () => {
        const jsonObject = {
            'Child 1': {
                'Grandchild 1': []
            },
            'Child 2': []
        };
        box.parseJsonToInteractiveBoxes(jsonObject);

        expect(box.childBoxes.length).toBe(2);
        expect(box.childBoxes[0].title).toBe('Child 1');
        expect(box.childBoxes[1].title).toBe('Child 2');
        expect(box.childBoxes[0].jsonChildren).toEqual({ 'Grandchild 1': [] });
    });

    // ...add more tests as needed
});
