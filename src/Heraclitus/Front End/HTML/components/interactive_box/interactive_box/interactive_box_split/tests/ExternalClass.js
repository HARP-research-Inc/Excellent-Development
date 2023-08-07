// ExternalClass.js
const $ = require('jquery');

class ExternalClass {
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

// ExternalClass.js

class ExternalClassDolla {
    constructor($) {
        this.$ = $;
        this.element = this.$('<div id="class-element"></div>');
    }

    appendElementToBody() {
        this.$('body').append(this.element);
    }

    removeElementFromBody() {
        this.$('#class-element').remove();
    }
}

module.exports = { ExternalClass, ExternalClassDolla};
