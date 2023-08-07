# HERACLITUS

Heraclitus is an innovative Excel add-in developed by HARP research. It's intended to drastically transform how companies process and interpret complex data by addressing the challenges inherent in spreadsheet usage. The key highlights include:

##### Polymorphic AI Integration: 
The foundation of Heraclitus is the proprietary polymorphic AI systems, capable of modifying their own structure to increase efficiency for repeated tasks and similar tasks. This sets HARP research ahead of competitors and provides approximately 2 million times more efficiency than traditional Large Language Models (LLMs).

##### Data Management: 
The Heraclitus add-in enables users to effectively manage and manipulate their data. This includes performing tasks such as data analysis, data cleaning, data transformation, and data visualization.

##### User Interface (UI):
Heraclitus provides a simple and user-friendly interface for all users. The main screen gives access to all primary functions including task creation, task history, and saved tasks. The task creation screen allows users to define tasks, specify datasets, and set task parameters. The task history screen displays a record of all past tasks. Lastly, the saved tasks screen provides access to all user-saved tasks for repeated use.

##### Efficiency and Automation:
Heraclitus is designed to enhance productivity by automating routine tasks. Users can save tasks that they frequently perform, saving time and reducing the chance of errors in the setup process.

##### Versatility:
It can be used in various fields that rely heavily on spreadsheet data such as finance, sales, HR, and more.

In summary, Heraclitus aims to revolutionize the way businesses handle spreadsheet data by providing a tool that combines AI-driven efficiency with intuitive functionality.

### Benefits:

- **Pain Point:** *Barriers to AI deployment in FinTech data processing*
**Solution Benefit:** *High Efficiency and Natural Language Interface*
The high efficiency of the polymorphic AI system combined with a natural language interface reduces the complexity of using AI in data processing. It requires fewer resources than typical AI systems, both in terms of computational power and human capital (specialized AI knowledge).

- **Pain Point:** *Privacy concerns due to cloud deployment*
**Solution Benefit:** *Secure Local Processing*
Your product runs on end-user hardware, which means all data can be processed locally without needing to be sent to the cloud. This drastically reduces privacy concerns as data remains within the user's environment.

- **Pain Point:** *Hallucinations when processing structured datasets*
**Solution Benefit:** *Accurate Processing*
Your Semantic Engine AI and S⁴ Neural Polymorphic Language have been designed to handle structured data accurately. By making all data and connections discrete, hallucinations (incorrect inferences made by AI) are effectively eliminated.

- **Pain Point:** *Expense of integration into end products*
**Solution Benefit:** *Affordable Solution*
Your revenue model is designed to scale with usage, making it accessible for a wide range of customers. The solution can be used as a stand-alone product or integrated as an add-in, making it flexible to different customer needs and budget sizes. Additionally, since the solution runs on end-user hardware, companies save on cloud storage and processing costs.

In summary, the product is designed to tackle the most significant obstacles that are currently preventing companies from leveraging the power of AI in their data processing tasks. Your system's high efficiency, local and secure processing, and accuracy combined with a scalable cost structure, makes it an attractive solution to the identified pain points.

## HERACLITUS Ribbon:

- **Home Screen:** This will be the main screen when the add-in is launched. It can include:
    + Button for opening a new task wizard.
    + Button for opening the saved tasks.
    + Button for accessing settings and help resources.

- **New Task Wizard:** This will guide the user through the process of setting up a new task. It can include:
- Data source selection: A screen to select the spreadsheet(s) to be processed.
- **Task configuration:** A screen to set up the task parameters, like the type of analysis or modification to be done.
- **Data privacy settings:** A screen to configure the security settings for the task.
- **Task review and confirmation:** A summary screen to review and confirm the task.
- **Saved Tasks:** This will be a screen where users can manage their saved tasks. It can include:

- **Task list:** A list of saved tasks, which can be edited, deleted, or run directly.
- **Task editor:** A screen to modify the parameters of a saved task.
- Settings and Help Resources: This will be a screen for configuring the add-in settings and accessing help resources. It can include:

- **Settings:** Options to configure the add-in behavior and appearance.
- **Help resources:** Links to user guides, tutorials, and FAQ.
- **Query Functionality:** A text box where users can input their queries in natural language. The AI will then provide the results based on its analysis of the spreadsheets.

- **Results Display:** A screen where the results of a task or query are displayed. It can include:

- **Summary:** A high-level summary of the results.
- **Detailed view:** An expandable view for detailed results.
- **Export:** Options to export the results to a file or another spreadsheet.
- **Notification Center:** A place where the add-in displays notifications, such as task completion alerts or errors.

In the context of the Heraclitus Excel add-in, a "task" refers to a specific operation or set of operations that the user wants to perform on their data. These tasks would be carried out by the polymorphic AI integrated into the add-in.

Examples of tasks could include:

- Data Analysis: The user might want to perform statistical analysis on their data, such as calculating averages, identifying outliers, or generating trend lines.

- Data Cleaning: The user might want to sanitize their data, such as removing duplicates, filling missing values, or normalizing inconsistent data.

- Data Transformation: The user might want to convert their data into a different format or structure, such as pivoting tables, splitting columns, or merging spreadsheets.

- Data Visualization: The user might want to create charts or graphs based on their data, such as bar charts, scatter plots, or heat maps.

- Advanced Analytics: The user might want to run more complex analyses on their data, such as machine learning models, predictive analytics, or trend forecasting.

Each of these operations would be considered a "task" in the context of the Heraclitus add-in. Users could potentially save these tasks if they plan to run them frequently, which would save time and reduce the chance of errors in the setup process. The saved tasks would be managed from the "Saved Tasks" screen in the proposed UI design.

# DEVPLAN

Must use VS for Excel implementation, Google Apps Script for Sheets

## P0
### Implementation of base functionality in sidebar:
---
Sidebar will include:
 EXCELLENT HERACLITUS logo

Database Tab:
  -  A list of IP addresses of databases
  -  You can click on one of them
  -  There is a plus button to add a new database
  -  There is a "add sheet to database" button
  -  There is a "add sheet to database" button
  - Each database has a dropdown with all the spreadsheets, and heirarical data in it each spreadsheet json
  - Import Database button, which will import from json
  - Export Database button, which will export to json

Greyed out Tasks tab, since the feature isnt yet implemented

HARP research logo and copyright

## P1
### Implementation of base assisstant in sidebar:
---
Assisstant: 
 - a chinbar in the sidebar with a text entry and a chat interface. Responses are sent to the data output, which is a mini spreadsheet of the output data, whether its a table or a value, with a paste into sheet button which will paste the result into a sheet at a given location

## P2
### Authentication and Login 
---
- settings button to right of logo
- settings screen with 
    + default username and password
    + dark or light mode
    + auto-login to all databases, default on

- Login button below databases
    + if login fails, offer to set different credentials

- credentials button next to login button
    + opens popup to change crendentials for individual credentials

## P3
### Version History
---
- add edit histoy option switch below dbs to allow to turn on or off edit history between users
- add show history to show all modifications with timestamps in the dropdowns

## P4
### Tasks
---
- add tasks tab with automated tasks option
figure out when we get here, work towards autodashboard
