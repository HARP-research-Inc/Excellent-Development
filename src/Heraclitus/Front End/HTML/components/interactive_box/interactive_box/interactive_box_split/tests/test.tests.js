const { JSDOM } = require("jsdom");
const jQuery = require("jquery");
let $;

const dom = new JSDOM(`...`);
const window = dom.window;
$ = jQuery(window);
global.jQuery = $;

beforeAll(async () => {
    const dom = await JSDOM.fromFile("index.html", {});
    const window = dom.window;
    const navigator = window.navigator;
    $ = jQuery(window);

    // Add jQuery, document, window, and navigator to the global scope
    global.jQuery = $;
    global.document = window.document;
    global.window = window;
    global.navigator = navigator;

    global.$ = $;
    require("jquery-ui-dist/jquery-ui");
    require("jquery-ui/ui/widgets/mouse");
    require("jquery-ui/ui/widgets/sortable");
});

describe("jQuery UI", () => {
    let testElement;

    
    test('test test', () => {
        expect(true).toBe(true);})

    
    beforeEach(() => {
        testElement = $("<div>").appendTo(document.body);
    });

    afterEach(() => {
        testElement.remove();
    });

    test(".resizable() method", () => {
        testElement.resizable();
        expect(testElement.hasClass("ui-resizable")).toBeTruthy();
    });
});
