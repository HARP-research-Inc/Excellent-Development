# iBox Component

Interactive-Box (iBox): A modular, nestable component allowing for an editable visualization of a tree structure.

## Structure:

* **Backplate (div)** : The body in which the iBoxes are placed and manipulated.
* **Expanded State** :
  * **iBox (div)** : The base box component, which has the following child elements:
  * **Corner-Box (div)** : The area where the label of the box and the drag handle reside. This sits above any other contents in the top left corner.
  * **Drag Handle (div)** : The area where the user can click and drag to move the entire iBox.
  * **Label (h element)** : Text which, when clicked, opens up a text entry field for the user to edit.
  * **Collapse Button (div)** : A "-" symbol in the top right corner that, when clicked, collapses the iBox.
  * **iBox (div, child)** : Another iBox nested within the parent iBox, allowing for a tree structure.
* **Collapsed State** :
  * **iBox (div)** : The base box in its collapsed state. It contains:
  * **Corner-Box (div)** : The area where the label of the box and the drag handle reside, above any other contents in the top left corner.
  * **Drag Handle (div)** : The area where the user can click and drag to move the entire iBox.
  * **Label (h element)** : Text which, when clicked, opens up a text entry field for the user to edit.
  * **Expand Button (div)** : A "+" symbol in the top right corner that, when clicked, expands the iBox.

## Behavior:

* **Resize** : The edges and the bottom right corner of the iBox can be dragged to resize it.
* **Move** : The drag handle can be used to move the iBox around within its parent container.
* **Edit** : The label text can be clicked on to open a text entry field. After pressing enter or clicking out, the label text will be updated and the width of the iBox will be adjusted accordingly.
* **Min Width** : The iBox has a minimum width of 103px plus the size of the corner box. This ensures that all elements within the iBox remain visible and accessible.
* **Expand/Collapse** : The iBox can be expanded and collapsed using the "+" or "-" buttons respectively. When collapsed, only the header (corner-box) is visible. When expanded, any child iBoxes become visible.
* **Animation** : The expansion and collapse of the iBox occur through smooth animations. The collapse animation reduces the size of the iBox until only the corner-box is visible. Conversely, the expand animation gradually increases the size of the iBox to reveal any nested child iBoxes.
* **Draggability** : Each iBox is draggable within its parent container. This allows users to rearrange the tree structure interactively. Draggability is enabled through the drag handle in the corner-box of each iBox.
* **Droppability** : Each iBox is droppable, meaning that other iBoxes can be dropped onto it. If an iBox is dropped onto another, it becomes a child of the iBox it was dropped onto. This allows users to dynamically nest the iBoxes and create a tree structure.
* **Child Generation** : An iBox can generate child iBoxes. This is achieved through the addChildBox() function in the iBox code. When this function is called, a new iBox is created and added to the parent iBox's childBoxes array. The new child iBox is then rendered within the parent iBox.
* **Visibility** : When an iBox is expanded, all of its child iBoxes become visible. When it is collapsed, all of its child iBoxes become hidden. This allows users to navigate through the tree structure by expanding and collapsing the iBoxes as needed. The visibility of child iBoxes is controlled through the collapse and expand buttons, and the state of the parent iBox.
* **Color Selection** : A predefined list of color templates is available for the user to choose from when creating an iBox. The user can select the desired color template from a dropdown menu or similar interface, and the selected color template will be applied to the iBox. The color templates define the colors used for the iBox's main body, header, and text.
* **JSON Representation** : When a child iBox is dropped into or added to a parent iBox, the parent iBox's JSON representation is updated to include the new child iBox. This JSON representation provides a structured, machine-readable description of the iBox hierarchy, and can be used to save and load the iBox structure.

## Interaction:

* **Click** : Clicking on the label text will open a text entry field that allows the user to edit the label. Clicking on the collapse or expand button will collapse or expand the iBox, respectively. Clicking anywhere else on the iBox will bring it to the front of the view.
* **Drag** : The user can click and drag the drag handle to move the iBox around within its parent container. The user can also drag the edges or bottom right corner of the iBox to resize it.
* **Drop** : If the user drags an iBox and drops it onto another, the dragged iBox will become a child of the iBox it was dropped onto.
* **Keyboard Input** : When the label text is being edited, the user can press enter to save the changes and update the label. If the user clicks outside of the text entry field, the changes will also be saved and the label updated.
* **Mouse Over** : When the user hovers the mouse over the collapse or expand button, the button will highlight to indicate that it is clickable. Similarly, when the user hovers over the drag handle or the edges of the iBox, the cursor will change to indicate that the iBox can be moved or resized.

## Children and JSON Functionality:

Each iBox can have multiple child iBoxes, enabling the creation of a tree structure. Child iBoxes are nested within their parent iBox, and can be added dynamically using the `addChildBox()` function. This function creates a new iBox, adds it to the parent iBox's `childBoxes` array, and then renders the new child iBox within the parent iBox.

Child iBoxes are rendered within their parent iBox when the parent iBox is expanded, and are hidden when the parent iBox is collapsed. This allows users to navigate through the tree structure by expanding and collapsing iBoxes as needed.

The iBox structure can also be constructed from a JSON object. The `parseJsonToInteractiveBoxes()` function takes a JSON object as an argument and recursively generates iBoxes for each JSON element. If the JSON element is an array, it creates an iBox for each element in the array. If the JSON element is an object, it creates an iBox for each key-value pair, with the key being the iBox title and the value being the child iBoxes. This function enables the dynamic generation of a tree structure of iBoxes based on a given JSON object.

When a new child iBox is added to a parent iBox (either manually by the user or programmatically through the `addChildBox()` function), the parent iBox's JSON representation is updated to include the new child iBox. This ensures that the JSON representation always accurately reflects the current state of the iBox hierarchy.

Styles:

* **.interactive-box** : Represents an interactive box with a width of 235px, height of 200px, and padding of 0px. The box has a 3px border radius, is positioned relatively, has a border and background color of #FF7E7E and #FFF3F3, respectively. The overflow content is hidden, with a margin of 10px. The bottom right and top left corners are more rounded with a border radius of 15px.
* **.drag-handle** : Specifies that the mouse cursor will change to a "resize" icon when hovering over elements with this class, indicating to users that they can click and drag to resize the box.
* **.corner-box** : Represents the top left corner of the interactive box, with a minimum width of 80px and a minimum height of 30px. The background color matches the border color of the interactive box, with a border of the same color. The bottom right corner is rounded with a border radius of 10px. The content is flex-aligned to space between, with a font size of 1.1em in Helvetica.
* **.corner-box span** : Specifies the style of the label text within the corner box. The text is vertically aligned in the middle, does not wrap to a new line, and is white in color with an Arial font.
* **.corner-input** : Represents the text input field that appears when the user clicks on the label text to edit it. Positioned at the top left corner of the box, with a left margin of 30px. It has a width of 70px, height of 35px, and a font size of 1.1em. The input field has no border, padding, or margin, and text is aligned to the left.
* **.expand-button, .collapse-button** : These classes define the styles for the expand and collapse buttons respectively. They have a padding of 5px at the top and bottom, and 15px on the right and 5px on the left. The buttons have a transparent background, no border, and a cursor that changes to a "pointer" when hovered over. The font size is 1.5em.
* **.collapse-button** : Specifies additional styles for the collapse button. Positioned at the top right corner of the box and colored a dark shade of red (#A95454).
* **.expand-button** : Specifies additional styles for the expand button. Vertically aligned in the middle and has a left margin of 115px and a right margin of -15px.

## Component Breakdown

Based on the comprehensive description, we can break down the iBox component into modular classes and components, and then describe how these can be expanded into additional functionality. I'll outline this from the base elements to the final culminating class, considering testability with jest unit and integration testing.

### Base Components

1. **Backplate Component** : Represents the body for iBoxes.
2. **iBox Component** : Includes both expanded and collapsed states. This is the base component for each iBox.
3. **Corner-Box Component** : Encapsulates the label, drag handle, collapse, and expand buttons.
4. **Drag Handle Component** : Allows drag-and-drop functionality.
5. **Label Component** : Provides editing functionality.
6. **Collapse Button and Expand Button Components** : Allow expansion and collapse.

### Class Expansions

1. **Resizable iBox (Inherits iBox)** :

* Adds resizing functionality.
* Contains handle for resizing at edges and bottom right corner.

1. **Draggable iBox (Inherits Resizable iBox)** :

* Enhances with drag-and-drop functionality.
* Uses Drag Handle Component.

1. **Editable iBox (Inherits Draggable iBox)** :

* Provides editing functionality for labels.

1. **Animatable iBox (Inherits Editable iBox)** :

* Adds expand and collapse animations.

1. **Droppable iBox (Inherits Animatable iBox)** :

* Allows other iBoxes to be dropped into it, supporting nesting.

1. **Generative iBox (Inherits Droppable iBox)** :

* Enables the generation of child iBoxes.

1. **ColorSelectable iBox (Inherits Generative iBox)** :

* Adds a color selection functionality for user customization.

1. **JSONInteractable iBox (Inherits ColorSelectable iBox)** :

* Enables interaction with JSON representation for saving and loading structure.

### Culminating Class

 **InteractiveBox (Inherits JSONInteractable iBox)** :

* The final class that incorporates all previous functionalities.
* Contains all properties and methods required for full behavior and interaction as described.

### Jest Unit and Integration Testing

By breaking down into smaller classes and components, we ensure that each piece can be tested independently. For instance:

1. **Unit Testing** :

* Test each base component separately (e.g., iBox, Corner-Box, Drag Handle).
* Test each class expansion, ensuring that it behaves as expected when the specific functionality is added.

1. **Integration Testing** :

* Test how the components work together within each expansion.
* Test the complete functionality within the culminating InteractiveBox class.

### Conclusion

The modular approach aligns well with modern software development principles and will help in maintaining, scaling, and testing the code efficiently. By segregating functionality into isolated components and layered class expansions, the development process becomes more flexible and allows for easier debugging and extension.

### File Structure:



```mathematica
iBox
│
├── src
│   ├── base
│   │   ├── iBoxBase.js
│   │   └── styles.css
│   │
│   ├── expansions
│   │   ├── Draggable.js
│   │   ├── Resizable.js
│   │   ├── Editable.js
│   │   └── ExpandCollapse.js
│   │
│   ├── components
│   │   └── iBoxComplete.js
│   │
│   ├── utils
│   │   ├── constants.js
│   │   └── helpers.js
│   │
│   └── index.js
│
├── test
│   ├── iBoxBase.test.js
│   ├── Draggable.test.js
│   ├── Resizable.test.js
│   ├── Editable.test.js
│   ├── ExpandCollapse.test.js
│   └── iBoxComplete.test.js
│
├── examples
│   ├── baseExample.html
│   ├── draggableExample.html
│   ├── resizableExample.html
│   ├── editableExample.html
│   ├── expandCollapseExample.html
│   └── completeExample.html
│
├── package.json
│
└── README.md
```

```

#### 1. `src` (Source Folder)

* `base` (Base Component Folder)
  * `iBoxBase.js`: Base iBox component, containing the minimal functionality of the iBox without any expansions.
  * `styles.css`: Base styling for the iBox component.
* `expansions` (Functionality Expansions Folder)
  * `Draggable.js`: Draggable functionality expansion.
  * `Resizable.js`: Resizable functionality expansion.
  * `Editable.js`: Editable functionality expansion.
  * `ExpandCollapse.js`: Expand and collapse functionality expansion.
* `components` (Complete Components Folder)
  * `iBoxComplete.js`: Culminating class that includes all previous functionality, integrating the base and all expansions.
* `utils` (Utilities Folder)
  * `constants.js`: Constants and configurations.
  * `helpers.js`: Helper functions to support main components.
* `index.js`: Entry point for the package/library.

#### 2. `test` (Test Folder)

* `iBoxBase.test.js`: Jest unit tests for the base iBox component.
* `Draggable.test.js`: Jest unit tests for the draggable functionality.
* `Resizable.test.js`: Jest unit tests for the resizable functionality.
* `Editable.test.js`: Jest unit tests for the editable functionality.
* `ExpandCollapse.test.js`: Jest unit tests for the expand/collapse functionality.
* `iBoxComplete.test.js`: Jest integration tests for the complete iBox component.

#### 3. `examples` (Examples Folder)

* `baseExample.html`: Example HTML file to test and interact with the base iBox component.
* `draggableExample.html`: Example HTML file to test and interact with the draggable functionality.
* `resizableExample.html`: Example HTML file to test and interact with the resizable functionality.
* `editableExample.html`: Example HTML file to test and interact with the editable functionality.
* `expandCollapseExample.html`: Example HTML file to test and interact with the expand/collapse functionality.
* `completeExample.html`: Example HTML file to test and interact with the complete iBox component.

#### 4. `package.json`: Lists dependencies and scripts for the project.

#### 5. `README.md`: Documentation for the project.

### Dependencies:

* **React** : For building the component.
* **Styled-Components** : For styling.
* **Jest** : For testing.
* **React-Draggable** : If the native drag functionality is not sufficient, this library can be used for drag handling.

### Expected Output:

* **Base iBox Component** : The minimal iBox structure and functionality.
* **Functional Expansions** : Individual functionality extensions such as draggability, resizability, editability, etc.
* **Complete iBox Component** : A fully functional iBox with all expansions integrated.
* **Test Files** : Test HTML files will render the associated components or functionalities, allowing manual interaction.

### Test HTML Files:

The `examples` folder contains HTML files that allow you to manually interact with the iBox component and its functionality expansions. Each file includes a minimal setup with necessary scripts to render the specific component or functionality for exploration and manual testing.

The implementation of these test files would include importing the specific component and any associated styles, initializing the component with desired properties, and including any additional scripts or HTML required to demonstrate the functionality.

These HTML files would facilitate hands-on exploration and provide a tangible understanding of how each component or functionality behaves, aiding in development, debugging, and user experience design.
