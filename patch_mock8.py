import re

with open("bible.html", "r") as f:
    html = f.read()

# Let's change the scroll effect to prioritize translation lookup FIRST.
# Because the user explicitly requests KJV/LSV verse IDs!
search_effect = """          // First try exact match (in case it IS an original vid or URL match)
          if (sortedVids.includes(targetScrollVerse)) {
              resolvedVid = targetScrollVerse;
              console.log("Resolved via exact match:", resolvedVid);
          } else {
              // Otherwise, targetScrollVerse might be requested based on KJV/LSV.
              // We search verseMap to see if the focalTranslation (or any translation) has a matching displayVid.
              // e.g. targetScrollVerse = "PSA.51.1"
              for (const vid of sortedVids) {
                  const translations = verseMap[vid];
                  if (!translations) continue;

                  // Check focal first
                  if (focalTranslation && translations[focalTranslation]?.displayVid === targetScrollVerse) {
                      resolvedVid = vid;
                      break;
                  }

                  // Fallback to checking any translation
                  for (const key in translations) {
                      if (translations[key]?.displayVid === targetScrollVerse) {
                          resolvedVid = vid;
                          break;
                      }
                  }
                  if (resolvedVid) {
                      console.log("Resolved via translation displayVid:", resolvedVid);
                      break;
                  }
              }
          }"""

replace_effect = """          // targetScrollVerse is usually requested based on KJV/LSV from the dialog.
          // We search verseMap to see if the focalTranslation (or any translation) has a matching displayVid.
          // e.g. targetScrollVerse = "PSA.51.1"
          for (const vid of sortedVids) {
              const translations = verseMap[vid];
              if (!translations) continue;

              // Check focal first
              if (focalTranslation && translations[focalTranslation]?.displayVid === targetScrollVerse) {
                  resolvedVid = vid;
                  break;
              }

              // Fallback to checking any translation
              for (const key in translations) {
                  if (translations[key]?.displayVid === targetScrollVerse) {
                      resolvedVid = vid;
                      break;
                  }
              }
              if (resolvedVid) {
                  console.log("Resolved via translation displayVid:", resolvedVid);
                  break;
              }
          }

          // Fallback to exact match (in case it IS an original vid or URL match)
          if (!resolvedVid && sortedVids.includes(targetScrollVerse)) {
              resolvedVid = targetScrollVerse;
              console.log("Resolved via exact match:", resolvedVid);
          }"""

html = html.replace(search_effect, replace_effect)

with open("bible.html", "w") as f:
    f.write(html)
