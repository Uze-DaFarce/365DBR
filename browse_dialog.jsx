// --- BIBLE BROWSE DIALOG ---
function BibleBrowseDialog({ isOpen, onClose, index, availableBooks, onSelect }) {
    // Pages/Steps: 'testament', 'book', 'chapter', 'verse'
    const [step, setStep] = useState('testament');
    const [book, setBook] = useState(null);
    const [chapter, setChapter] = useState(null);
    const [sortDesc, setSortDesc] = useState(false);

    // Chunking state
    const [chapterGroupIndex, setChapterGroupIndex] = useState(0);
    const [verseGroupIndex, setVerseGroupIndex] = useState(0);

    const [testament, setTestament] = useState(null); // 'OT' or 'NT'

    // Reset when opened
    useEffect(() => {
        if (isOpen) {
            setStep('testament');
            setTestament(null);
            setBook(null);
            setChapter(null);
            setSortDesc(false);
            setChapterGroupIndex(0);
            setVerseGroupIndex(0);
        }
    }, [isOpen]);

    if (!isOpen) return null;

    const handleBookSelect = (b) => {
        setBook(b);
        setChapterGroupIndex(0);
        setStep('chapter');
    };

    const handleChapterSelect = (c) => {
        setChapter(c);
        setVerseGroupIndex(0);

        // If we have index data and there's only 1 verse in this chapter, auto-select it
        if (index && index[book] && index[book][c]) {
            const verses = index[book][c];
            if (verses.length === 1) {
                onSelect(book, c, verses[0]);
                onClose();
                return;
            }
        }
        setStep('verse');
    };

    const handleVerseSelect = (v) => {
        onSelect(book, chapter, v);
        onClose();
    };

    const handleBack = () => {
        if (step === 'verse') setStep('chapter');
        else if (step === 'chapter') setStep('book');
        else if (step === 'book') setStep('testament');
    };

    const OT_BOOKS = availableBooks.slice(0, 39);
    const NT_BOOKS = availableBooks.slice(39);

    const handleTestamentSelect = (t) => {
        setTestament(t);
        setStep('book');
    };

    // Prepare data for current view
    let displayBooks = [];
    if (step === 'book') {
        displayBooks = testament === 'OT' ? OT_BOOKS : NT_BOOKS;
        if (sortDesc) {
            displayBooks = [...displayBooks].sort((a, b) => BOOK_NAMES[a].localeCompare(BOOK_NAMES[b]));
        }
    }

    let chapterChunks = [];
    let currentChapterChunk = [];
    const CHUNK_SIZE = 70; // 35 per page

    if (step === 'chapter' && index && index[book]) {
        let chapters = Object.keys(index[book]).map(Number);
        chapters.sort((a,b) => a - b);

        for (let i = 0; i < chapters.length; i += CHUNK_SIZE) {
            chapterChunks.push(chapters.slice(i, i + CHUNK_SIZE));
        }
        currentChapterChunk = chapterChunks[chapterGroupIndex] || [];
    }

    let verseChunks = [];
    let currentVerseChunk = [];
    if (step === 'verse' && index && index[book] && index[book][chapter]) {
        let verses = index[book][chapter].map(Number);
        verses.sort((a,b) => a - b);

        for (let i = 0; i < verses.length; i += CHUNK_SIZE) {
            verseChunks.push(verses.slice(i, i + CHUNK_SIZE));
        }
        currentVerseChunk = verseChunks[verseGroupIndex] || [];
    }

    // Layout logic
    const isSplitLayout = true; // Always two pages

    // Helper to split a chunk into two columns (Left Page / Right Page)
    const splitArray = (arr) => {
        const mid = Math.ceil(arr.length / 2);
        return [arr.slice(0, mid), arr.slice(mid)];
    };

    const [leftBooks, rightBooks] = step === 'book' ? splitArray(displayBooks) : [[], []];
    const [leftChapters, rightChapters] = step === 'chapter' ? splitArray(currentChapterChunk) : [[], []];
    const [leftVerses, rightVerses] = step === 'verse' ? splitArray(currentVerseChunk) : [[], []];


    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-2 sm:p-4 md:p-10 bg-black/60 backdrop-blur-sm transition-opacity">
            <div className={`bg-stone-50 w-full ${step === 'testament' ? 'max-w-3xl' : 'max-w-5xl'} h-[90vh] md:h-[80vh] rounded-2xl md:rounded-3xl shadow-2xl flex flex-col overflow-hidden relative border border-stone-200 transition-all duration-300`}>

                {/* Header / Controls */}
                <div className="absolute top-0 inset-x-0 h-16 md:h-20 bg-gradient-to-b from-stone-200/80 to-transparent flex items-center justify-between px-4 md:px-8 z-20 pointer-events-none">
                    <div className="flex-1 pointer-events-auto flex items-center gap-2">
                        {step !== 'testament' && (
                            <button onClick={handleBack} className="hidden md:flex items-center gap-1 text-stone-500 hover:text-amber-700 font-bold text-xs uppercase tracking-wider bg-white/50 hover:bg-white px-3 py-1.5 rounded-full transition-all border border-stone-200 shadow-sm focus:outline-none focus:ring-2 focus:ring-amber-500">
                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
                                Back
                            </button>
                        )}
                    </div>

                    <div className="flex-1 flex justify-center pointer-events-auto items-center gap-4">
                        {/* Book Name in Header for Chapter/Verse Views */}
                        {(step === 'chapter' || step === 'verse') && book && (
                            <h2 className="hidden md:flex text-xl md:text-2xl font-serif font-black uppercase tracking-tight text-stone-800 bg-white/60 px-4 py-1.5 rounded-xl shadow-sm border border-stone-200 backdrop-blur-md">
                                {BOOK_NAMES[book]}
                                {step === 'verse' && <span className="text-stone-500 ml-2 font-sans text-lg self-center">{chapter}</span>}
                            </h2>
                        )}

                        {step === 'book' && (
                            <button onClick={() => setSortDesc(!sortDesc)} className="flex items-center gap-1 text-stone-600 hover:text-amber-700 font-bold text-[10px] md:text-xs uppercase tracking-wider bg-white/80 hover:bg-white px-3 py-1.5 rounded-full transition-all border border-stone-200 shadow-sm focus:outline-none focus:ring-2 focus:ring-amber-500">
                                {sortDesc ? (<> <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" /></svg> A-Z </>) : (<> <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" /></svg> # </>)}
                            </button>
                        )}
                    </div>

                    <div className="flex-1 flex justify-end pointer-events-auto">
                        <button onClick={onClose} className="p-2 text-stone-400 hover:text-stone-700 bg-white/50 hover:bg-white rounded-full transition-all border border-transparent hover:border-stone-200 shadow-sm focus:outline-none focus:ring-2 focus:ring-amber-500" aria-label="Close dialog">
                            <svg className="h-5 w-5 md:h-6 md:w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                        </button>
                    </div>
                </div>

                {/* Main Content Area */}
                <div className={`flex-1 flex flex-col md:flex-row pt-14 md:pt-0`}>

                    {/* Mobile Header elements merged into content area */}
                    {step !== 'testament' && (
                        <div className="md:hidden px-4 pt-2 pb-0 flex items-center justify-between">
                            <button onClick={handleBack} className="flex items-center gap-1 text-stone-500 font-bold text-xs uppercase tracking-wider focus:outline-none">
                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
                                Back
                            </button>
                            {book && (
                                <span className="font-serif font-black uppercase tracking-tight text-stone-800 text-sm">
                                    {BOOK_NAMES[book]} {step === 'verse' && chapter}
                                </span>
                            )}
                        </div>
                    )}

                    {/* Book Cover Layout (Testament Step) */}
                    {step === 'testament' && (
                         <div className="flex-1 flex flex-col md:flex-row relative">
                            {/* Spine separator (Desktop only) */}
                            <div className="hidden md:block absolute top-0 bottom-0 left-1/2 w-px bg-stone-300 shadow-[0_0_15px_1px_rgba(0,0,0,0.1)] -translate-x-1/2"></div>

                            <div className="flex-1 p-8 md:p-12 flex flex-col justify-center bg-gradient-to-l from-stone-100/50 to-transparent">
                                <button onClick={() => handleTestamentSelect('OT')} className="w-full h-48 md:h-80 bg-amber-50 hover:bg-amber-100 border-2 border-amber-200 rounded-xl flex flex-col items-center justify-center gap-2 md:gap-4 transition-all hover:scale-[1.02] hover:shadow-lg text-amber-900 group">
                                    <span className="text-4xl md:text-5xl lg:text-6xl font-serif font-black uppercase tracking-tight group-hover:text-amber-700 transition-colors">Old</span>
                                    <span className="text-2xl md:text-3xl lg:text-4xl font-serif italic text-amber-700/70">Testament</span>
                                </button>
                            </div>

                            <div className="flex-1 p-8 md:p-12 flex flex-col justify-center bg-gradient-to-r from-stone-100/50 to-transparent">
                                <button onClick={() => handleTestamentSelect('NT')} className="w-full h-48 md:h-80 bg-blue-50 hover:bg-blue-100 border-2 border-blue-200 rounded-xl flex flex-col items-center justify-center gap-2 md:gap-4 transition-all hover:scale-[1.02] hover:shadow-lg text-blue-900 group">
                                    <span className="text-4xl md:text-5xl lg:text-6xl font-serif font-black uppercase tracking-tight group-hover:text-blue-700 transition-colors">New</span>
                                    <span className="text-2xl md:text-3xl lg:text-4xl font-serif italic text-blue-700/70">Testament</span>
                                </button>
                            </div>
                         </div>
                    )}

                    {/* Book / Chapter / Verse Views (Full Spread - Split Left/Right) */}
                    {step !== 'testament' && (
                        <div className="flex flex-col h-full w-full p-4 md:p-8 md:pt-20 bg-gradient-to-r from-stone-50 to-transparent overflow-y-auto min-h-[50vh]">

                             {/* Mobile Titles */}
                             <div className="md:hidden text-center mb-6 mt-4">
                                {step === 'book' && <h2 className="text-2xl font-serif font-black uppercase text-stone-800">Select Book</h2>}
                                {step === 'chapter' && <h2 className="text-xl font-serif font-black uppercase text-stone-800">Select Chapter</h2>}
                                {step === 'verse' && <h2 className="text-xl font-serif font-black uppercase text-stone-800">Select Verse</h2>}
                            </div>

                             {/* Chunk Selectors for Chapter/Verse */}
                             {(step === 'chapter' || step === 'verse') && (
                                <div className="flex flex-wrap gap-2 mb-6 justify-center sticky top-0 bg-stone-50/90 backdrop-blur pb-2 z-10 pt-2">
                                    {(step === 'chapter' ? chapterChunks : verseChunks).length > 1 && (step === 'chapter' ? chapterChunks : verseChunks).map((chunk, idx) => (
                                        <button key={idx} onClick={() => step === 'chapter' ? setChapterGroupIndex(idx) : setVerseGroupIndex(idx)} className={`px-4 py-1.5 rounded-full text-xs font-bold transition-colors ${(step === 'chapter' ? chapterGroupIndex : verseGroupIndex) === idx ? 'bg-amber-600 text-white shadow-md' : 'bg-white border border-stone-200 text-stone-600 hover:bg-stone-50'}`}>
                                            {`${chunk[0]}-${chunk[chunk.length-1]}`}
                                        </button>
                                    ))}
                                </div>
                            )}

                            {/* Split Content: Left Page / Right Page Container */}
                            <div className="flex flex-col md:flex-row flex-1 w-full relative">
                                {/* Spine separator (Desktop only) */}
                                <div className="hidden md:block absolute top-0 bottom-0 left-1/2 w-px bg-stone-300 shadow-[0_0_15px_1px_rgba(0,0,0,0.1)] -translate-x-1/2"></div>

                                {/* Left Page Bucket */}
                                <div className="flex-1 md:pr-8 lg:pr-12 md:pb-8">
                                    <div className={`grid ${step === 'book' ? 'grid-cols-3 sm:grid-cols-4 lg:grid-cols-4' : 'grid-cols-5 sm:grid-cols-6 lg:grid-cols-5'} gap-2 md:gap-3 content-start`}>
                                        {step === 'book' && leftBooks.map(b => (
                                            <button key={b} onClick={() => handleBookSelect(b)} className="bg-white border border-stone-200 hover:border-amber-400 hover:bg-amber-50 hover:shadow-md rounded-lg p-2 flex flex-col items-center justify-center transition-all focus:outline-none focus:ring-2 focus:ring-amber-500 group">
                                                <span className="text-lg md:text-xl font-black text-stone-800 group-hover:text-amber-700 uppercase">{b}</span>
                                                <span className="text-[9px] md:text-[10px] text-stone-500 truncate w-full text-center mt-1">{BOOK_NAMES[b]}</span>
                                            </button>
                                        ))}
                                        {step === 'chapter' && leftChapters.map(c => (
                                            <button key={c} onClick={() => handleChapterSelect(c)} className="bg-white border border-stone-200 hover:border-amber-400 hover:bg-amber-50 shadow-sm hover:shadow-md rounded-lg p-2 md:p-3 flex items-center justify-center font-bold text-lg text-stone-700 transition-all focus:outline-none focus:ring-2 focus:ring-amber-500">
                                                {c}
                                            </button>
                                        ))}
                                         {step === 'verse' && leftVerses.map(v => (
                                            <button key={v} onClick={() => handleVerseSelect(v)} className="bg-white border border-stone-200 hover:border-amber-400 hover:bg-amber-50 shadow-sm hover:shadow-md rounded-lg p-2 md:p-3 flex items-center justify-center font-bold text-lg text-stone-700 transition-all focus:outline-none focus:ring-2 focus:ring-amber-500">
                                                {v}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {/* Right Page Bucket */}
                                <div className="flex-1 md:pl-8 lg:pl-12 pt-4 md:pt-0">
                                    <div className={`grid ${step === 'book' ? 'grid-cols-3 sm:grid-cols-4 lg:grid-cols-4' : 'grid-cols-5 sm:grid-cols-6 lg:grid-cols-5'} gap-2 md:gap-3 content-start`}>
                                         {step === 'book' && rightBooks.map(b => (
                                            <button key={b} onClick={() => handleBookSelect(b)} className="bg-white border border-stone-200 hover:border-amber-400 hover:bg-amber-50 hover:shadow-md rounded-lg p-2 flex flex-col items-center justify-center transition-all focus:outline-none focus:ring-2 focus:ring-amber-500 group">
                                                <span className="text-lg md:text-xl font-black text-stone-800 group-hover:text-amber-700 uppercase">{b}</span>
                                                <span className="text-[9px] md:text-[10px] text-stone-500 truncate w-full text-center mt-1">{BOOK_NAMES[b]}</span>
                                            </button>
                                        ))}
                                        {step === 'chapter' && rightChapters.map(c => (
                                            <button key={c} onClick={() => handleChapterSelect(c)} className="bg-white border border-stone-200 hover:border-amber-400 hover:bg-amber-50 shadow-sm hover:shadow-md rounded-lg p-2 md:p-3 flex items-center justify-center font-bold text-lg text-stone-700 transition-all focus:outline-none focus:ring-2 focus:ring-amber-500">
                                                {c}
                                            </button>
                                        ))}
                                         {step === 'verse' && rightVerses.map(v => (
                                            <button key={v} onClick={() => handleVerseSelect(v)} className="bg-white border border-stone-200 hover:border-amber-400 hover:bg-amber-50 shadow-sm hover:shadow-md rounded-lg p-2 md:p-3 flex items-center justify-center font-bold text-lg text-stone-700 transition-all focus:outline-none focus:ring-2 focus:ring-amber-500">
                                                {v}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>

                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
// --- END BIBLE BROWSE DIALOG ---