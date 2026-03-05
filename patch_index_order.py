import re

with open("index.html", "r") as f:
    content = f.read()

# First, revert the previous swap I made so the DOM order is: Browse, Compare, Focal, Bookmarks, Desktop Listen
# Or wait, right now the DOM order is Browse, Compare, Focal, Bookmarks, Listen. Let's check!
