import re

with open("bible.html", "r") as f:
    html = f.read()

# Add logging to the scroll effect to see what's happening
search_effect = """          // First try exact match (in case it IS an original vid or URL match)
          if (sortedVids.includes(targetScrollVerse)) {
              resolvedVid = targetScrollVerse;
          } else {
              // Otherwise, targetScrollVerse might be requested based on KJV/LSV."""

replace_effect = """          console.log("targetScrollVerse:", targetScrollVerse);
          console.log("focalTranslation:", focalTranslation);

          // First try exact match (in case it IS an original vid or URL match)
          if (sortedVids.includes(targetScrollVerse)) {
              resolvedVid = targetScrollVerse;
              console.log("Resolved via exact match:", resolvedVid);
          } else {
              // Otherwise, targetScrollVerse might be requested based on KJV/LSV."""

html = html.replace(search_effect, replace_effect)

search_effect2 = """                  if (resolvedVid) break;
              }
          }

          if (resolvedVid) {"""

replace_effect2 = """                  if (resolvedVid) {
                      console.log("Resolved via translation displayVid:", resolvedVid);
                      break;
                  }
              }
          }

          if (resolvedVid) {"""
html = html.replace(search_effect2, replace_effect2)


with open("bible.html", "w") as f:
    f.write(html)
