
# EXCELLENT DEMO PLANNING

### p0) - Algo w/ AI: ~1.5 days
Use openai to make algorithm peices without doing it by hand.
- design total code  **✓**
- make classes and helpers
- design exmaples for each step in playground
- write code

#### Demo Outline:

- **Chunking + Labeling:** *Existing Chunking and Labeling Code*
- **gen_tree**
    <u>Methods:</u>
    + built-in csv translation
        - stores after ran once
    + store previous prompt data (csv's and heirarchies) 
    + cleaned heirarchy output
    + to-json method
    + get non-complete (missing t/b or l/r) tables
    + get prime width tables

    <u>Subclasses:</u>
    + **blocks**
        <u>Attributes:</u>
        - csv
        - size
        - start + end
        - cell_type
        - cell values
        - orientation

        <u>Methods:</u>
        - get_(attribute)
            *will store in attribute if gotten*
    + **tables**
        <u>Attributes:</u>
        - csv
        - size
        - start + end

        <u>Methods:</u>
        - get_(attribute)
            *will store in attribute if gotten*
        - cleaned heirarchy output
        - is_prime

- **prompt_interface**
    + pass in variable names
    + pass in tag names (html)
    + pass in examples, system message
    + check output for correct format
        - if no start tag:
            Try again x3, else fail
        - if no end tag:
            continue generating x3, check format, else fail
    + return result

- **SB_ID:**
    + take annotated json, pass in as free blocks to general tree
    + call csv-format method to get csv format for data
    + prompt: system: explain goal plus format, 4 examples: csv -> (start tag) heirerarchy out (end tag)
    + pass in to prompt_interface
    + pass output to class
- **ST_ID:**
    + take SBs in gtc as list and pass in to prompt
    + call csv-format method to get csv format for data for prompt
    + prompt: system: explain goal plus format, 10 examples: csv, sbs -> (overal start tag) (start tag) csv of table (end tag) (sb's tag) list of sbs in json (end sb's)... (overal end tag)
        - ANTI-EXAMPLES: light blocks
    + pass returned answer
- **ST_ID2:**
    + take heriarchy in gtc as list and pass in to prompt
    + get last set of csvs
    + prompt: system: explain goal plus format, 4 examples: overall csv, csvs, SBs -> (overal start tag) (start tag) csv of table tables (end tag) (tables tag) list of tables (end tables)... (overal end tag)
    + pass returned answer
- **LB_ID_LABEL:**
    + get csv of and around tables
    + pass with 4 examples and prompt
- **LB_ID_AB:**
    + get non-complete tables and all blocks around
    + 10 exmaples for prompt
        - 5 NON
        - 5 correct
    + pass AB csv with heirarchy for each
- **LB_ID_BB:**
    + get still non-complete tables and all blocks around
    + 10 exmaples for prompt
        - 5 NON
        - 5 correct
    + pass BB csv with heirarchy for each
- **LB_ID_CB:**
    + get still non-complete tables and all blocks around
    + 10 exmaples for prompt
        - 5 NON
        - 5 correct
    + pass CB csv with heirarchy for each, same convo
- **Pattern_Splitting:**
    + get non-prime data width tables
    + 5 examples for prompt
    + pass heirarchy + csv in, csv + heirarchy out
- **recursive_table_ID**
    + pass full heirarchy + csv in
    + 5 examples, (dont want confusion or huge data)
- **template_extraction**
    + pass class into template class, hidden data 
    + consider changing labels in patterns as DOF's with labels listed
- **Multi_DOF_comparison**
    + if multi-doc, check if diff templates
    + for each smallest part with difference in structure, but same position, pass full csv of both and templates of both into LLM
    + 10 examples 
    + retreive general template
- **Synthetic_Model**
    + general template + spreadsheets -> output json
    + pass template + spreadsheet to AI
    + 5 examples
    + retreive output json

### p1) - Static Demo: ~2 days
After making protoalgo, send email then make static visual framework for each step
- do D3.js tutorial
- 0 sheet chunking: chunked class
- annotated block ID: annotated class
- 1 solid block ID: block class
- 3 -> 9: standard class
- 10: spreadsheet input class + standard

### p1.5) - UI: ~0.5 days
After making static demo, add interaction elements:
- Upload
- Example spreadsheets
- next back button
- download

### p2) - Animated Demo: ~1days
After making visual, add animations

### p3) - Local AI: ~.25 days
After doing so, get local falcon model to run task

