# The playwright script fails because there is no text=Old Testament.
# Ah wait! It has:
# <span className="text-2xl md:text-3xl lg:text-4xl font-serif italic text-amber-700/70">Testament</span>
# <div className="absolute top-4 left-4 font-black uppercase tracking-widest text-amber-900/40 text-xs">Old</div>
# So the words "Old" and "Testament" are in different elements!
# Let's just click the button by finding the text "Old"
