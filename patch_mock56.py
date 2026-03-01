# Ah! The issue might be that `overflow-y-auto min-h-[50vh]` is NOT SCROLLING because its PARENT doesn't constrain its height!
# The parent is:
# `<div className="bg-stone-50 w-full max-w-5xl h-[90vh] md:h-[80vh] rounded-2xl md:rounded-3xl shadow-2xl flex flex-col overflow-hidden relative border border-stone-200 transition-all duration-300">`
# This parent uses `flex flex-col overflow-hidden`.
# The child uses `flex flex-col h-full w-full ... overflow-y-auto min-h-[50vh]`.
# A `h-full` child inside a flex-col parent SHOULD be constrained if the parent has a fixed height (`h-[90vh]`).
# So it should scroll.
# Maybe `el.scrollHeight` just didn't work. Let me manually scroll with the mouse.
