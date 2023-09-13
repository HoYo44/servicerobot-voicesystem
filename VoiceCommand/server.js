const express = require('express');
const app = express();
const PORT = 8080;

app.use(express.static('public'));  // 例: 'public'

app.listen(PORT, () => {
    console.log(`Server started on http://localhost:${PORT}`);
});
