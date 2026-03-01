// Let's test the processContent logic
function processContent(contentArray, map, versionKey, useOrgId = false) {
  if (!contentArray) return;
  const buffer = { text: [] };
  const context = { activeVid: null, lastSeenVid: null };
  function walkItems(items, map, versionKey, useOrgId, buffer, context) {
    if (!items) return;
    for (const item of items) {
      let previousActiveVid = context.activeVid;
      if (item.attrs?.verseId) {
        let keyVid = item.attrs.verseId;
        if (useOrgId && item.attrs.verseOrgIds && item.attrs.verseOrgIds.length > 0) keyVid = item.attrs.verseOrgIds[0];
        context.activeVid = keyVid;
        context.lastSeenVid = keyVid;
        if (!map[keyVid]) map[keyVid] = {};
        if (!map[keyVid][versionKey]) map[keyVid][versionKey] = { text: [], displayVid: item.attrs.verseId };
      }
      if (item.items && item.items.length > 0) walkItems(item.items, map, versionKey, useOrgId, buffer, context);
      context.activeVid = previousActiveVid;
    }
  }
  for (const section of contentArray) {
    if (section.items) walkItems(section.items, map, versionKey, useOrgId, buffer, context);
  }
}

let mockMap = {};
let mockContent = [
  { items: [ { attrs: { verseId: "GEN.1.2", verseOrgIds: ["b3b1..."] } } ] }
];

processContent(mockContent, mockMap, "original", false);
processContent(mockContent, mockMap, "kjv", true);
console.log(mockMap);
