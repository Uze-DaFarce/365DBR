# Ah, the test failed because there is no CORS allow header for `http://localhost:3000` to fetch `https://mt-sin.ai/365DBR/data/...`
# Let's run `python3 -m http.server 3000` and use `compile_site` or just generate the file.
# We don't need to test in playwright anymore because we literally saw the problem in the code:
# `setTargetScrollVerse(null)` was being called before `setTimeout` and `setTimeout` was completely absent!
