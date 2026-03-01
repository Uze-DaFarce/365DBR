# In `BibleBrowseDialog` the `flex-1 min-h-0` is added to the scroll container.
# Also `pt-20` is added on mobile because `mt-4` and `md:pt-20` meant that on mobile, the header (`h-16`) was overlapping the content!
# In the `BibleBrowseDialog` component:
# `<div className="absolute top-0 inset-x-0 h-16 md:h-20 bg-gradient-to-b from-stone-200/80 to-transparent flex items-center justify-between px-4 md:px-8 z-20 pointer-events-none">`
# This header has `h-16` on mobile. So we need `pt-20` on the scroll container to push content below the absolute header.

# Let's verify the scrolling again!
