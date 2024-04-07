const express = require('express');
const path = require('path');
const app = express();

app.use(express.static('pythonHTMLGen'));
app.listen(8000, () => {
    console.log("App listening on port 8000");
})