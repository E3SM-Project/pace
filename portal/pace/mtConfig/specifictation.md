# modelTiming.py configuration files
These files tell modelTiming.py what to look for in a GPTL file in order to describe what it is, as well as parse it. They allow a user to make their own "GPTL-like" files.

# Requirements:
A single file is written in JSON, containing an array of objects that contain the following values to assist in parsing the file:

Value | Syntax/variable type | Description
------|----------------------|------------
names | *Array of strings* | list of names for each value (in order) These are the exact names printed from gptl, and can be used to search for a file type. (Can be left empty, but may leave out clues if so)
altNames | *Array of strings* | alternate names (If originals don't make sense in a programatic context) (can be left empty if names are filled in, individual names can be a null value)
startMarker | `["marker",1]` | Look for index 1, if you find it, jump <index 2> lines down to start reading the information for that thread.
fileIdentifiers | *Array of strings* | These tell the parser if this configuration matches the file it's looking at. If one is found, it will use this configuration as the reference to read in the data (Not required if "startMarker" exists)
rootParent | integer | This is the minimum indention the process list uses to display its data.