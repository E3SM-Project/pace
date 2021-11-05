# modelTiming.py configuration files
These files tell modelTiming.py what to look for in a GPTL file in order to describe what it is, as well as parse it. They allow a user to make their own "GPTL-like" files.

For an example of how to make/use one, see [The sample config](./testConfig.json), and [The sample file](./testFile.txt)

# Requirements:
A single file is written in JSON. It starts with an object containing names of categories that a configuration could fall into (e.g this project was desgined to look at E3SM model timing files, so they fall under the category `e3sm`). That category in itself is an object containing a list of configurations, each with the following properties:

Value | Syntax/variable type | Description
------|----------------------|------------
fileCols | *Array of strings* | list of names for each value (in order) These are the exact names printed from gptl, and can be used to search for a file type. Not all names need to be here, and the list itself can even be left empty. *The more names inserted here, the easier it is to detect the file.*
outCols | *Array of strings* | **(Required)** Names the parser uses when exporting the GPTL files to other formats. They need to be the exact number of variables displayed in the file per row (Not including name)
startMarker | `["marker",1]` | Look for index 1, if you find it, jump <index 2> lines down to start reading the information for that thread.
fileIdentifiers | *Array of strings* | These tell the parser if this configuration matches the file it's looking at. If one is found, it will use this configuration as the reference to read in the data.
rootParent | integer | This is the minimum indention the process list uses to display its data.

## Additional notes
* Because of the way an entire tree is scanned, the file can have plain text virtually anywhere inside of it (except within the body of a tree). This is good for making comments within a file.
* If you're writing an mt file, be sure to end a thread/tree by starting a blank line and hitting return/enter (`\n`)
* As of this writing, mutliple thread types in one file is not yet supported.
* If there are extremely similar configurations within the same category, the best way to detect everything is to place the categories with the most names or fileIdentifiers on top.
