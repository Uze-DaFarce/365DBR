# The images are cut off at the bottom!
# Ah, looking at `mobile_dialog_chapters.png`, the scroll container might not actually be scrolling!
# Notice how the modal itself has a rounded bottom, but it's floating.
# It uses `h-[90vh] md:h-[80vh]`. This means it occupies 90% of the viewport height on mobile.
# However, the user said "The dialog is so massive on the phone you can only choose Old Testament. No way to scroll... It doesn't fit the screen even when holding the phone completely sideways."
# If I look at the Testament image: The "New Testament" button is completely missing!
# Let me look at the Testament image again. Yes! You only see the "OLD Testament" button!
# Why?
# `<div className="flex-1 flex flex-col md:flex-row relative">`
# `<div className="flex-1 p-8 md:p-12 flex flex-col justify-center bg-gradient-to-l from-stone-100/50 to-transparent">`
# Inside it: `<button className="w-full h-48 md:h-80 ...">`
# The problem is that the Testament container (`flex-col md:flex-row`) is inside a parent that has NO scrolling.
# In `BibleBrowseDialog`:
# `<div className="...">`
#   `{step === 'testament' && ( ... flex-1 flex flex-col ... )}`
#   `{step !== 'testament' && ( ... overflow-y-auto ... )}`
#
# Ah! `step === 'testament'` has NO `overflow-y-auto`! It is hardcoded to `h-[90vh]` and the two `h-48` blocks plus padding exceed the viewport, cutting off the second button completely without a scrollbar!
# Wait, and what about landscape mode? "It doesn't fit the screen even when holding the phone completely sideways."
# In landscape, viewport height is small (e.g., 375px height). `h-[90vh]` is only 337px. But the two buttons stack vertically because `md:` breakpoint (768px) is usually wider, but wait, landscape on some phones is wider than 768? No, iPhone landscape is 812x375 (width x height).
# So `md:` (768px width) MIGHT trigger in landscape, but then it puts them side-by-side (`md:flex-row`). BUT `h-80` (320px) is too tall for a 337px container with header padding.
# And without `overflow-y-auto`, you can't scroll at all!

# Let's fix the layout classes!
