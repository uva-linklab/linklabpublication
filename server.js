const express = require("express");
const path = require("path");

const app = express();
const PORT = 3000; 

app.use("/static", express.static(path.join(__dirname, "src", "static")));
app.use("/config", express.static(path.join(__dirname, "src", "config")));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "src", "templates", "index.html"));
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
