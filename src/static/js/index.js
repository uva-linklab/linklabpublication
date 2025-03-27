let authors = [];
let publications = [];
let currentPage = 1;
let itemsPerPage = 20;

// Helper function to get query parameters
function getQueryParams() {
  const params = new URLSearchParams(window.location.search);
  return Object.fromEntries(params.entries());
}

// Helper function to set query parameters
function setQueryParams(params) {
  const query = new URLSearchParams(params).toString();
  history.replaceState(null, "", "?" + query);
}

// Load filters from URL parameters on page load
function loadFiltersFromURL() {
  const params = getQueryParams();

  // Set the search term
  if (params.search) {
    document.getElementById("search").value = params.search;
  }

  // Pre-select filters based on URL parameters
  if (params.author) {
    document.getElementById("filterAuthor").value = params.author;
  }
  if (params.year) {
    document.getElementById("filterYear").value = params.year;
  }
  if (params.journal) {
    document.getElementById("filterJournal").value = params.journal;
  }

  // Set pagination parameters
  if (params.page) {
    currentPage = parseInt(params.page, 10) || 1;
  }
  if (params.itemsPerPage) {
    itemsPerPage = parseInt(params.itemsPerPage, 10) || 20;
  }
}

// Update URL parameters when filters or pagination change
function updateURLParams() {
  const params = {
    search: document.getElementById("search").value.trim(),
    author: document.getElementById("filterAuthor").value,
    year: document.getElementById("filterYear").value,
    journal: document.getElementById("filterJournal").value,
    page: currentPage,
    itemsPerPage: itemsPerPage,
  };

  // Remove empty parameters
  Object.keys(params).forEach((key) => {
    if (!params[key]) delete params[key];
  });

  const query = new URLSearchParams(params).toString();
  history.replaceState(null, "", "?" + query);
}

// Load authors and publications dynamically
async function loadData() {
  // const authorResponse = await fetch("authors.json");
  const authorResponse = await fetch("/config/authors.json");

  authors = await authorResponse.json();

  // const bibResponse = await fetch("pub.bib");
  const bibResponse = await fetch("/static/bib/Publications.bib");
  const bibText = await bibResponse.text();
  publications = parseBibTeX(bibText);

  populateFilters();
  loadFiltersFromURL();
  renderPublications();
}
function parseBibTeX(bibText) {
  console.log("BibTeX File Content:", bibText);

  // Match all BibTeX entries with multiline support and nested braces handling
  const entries = bibText.match(/@\w+\s*{[^@]*}/gs) || [];
  console.log("Matched BibTeX Entries:", entries);

  const publications = [];

  entries.forEach((entry, index) => {
    try {
      // Extract entry type (e.g., @journalarticle)
      const typeMatch = entry.match(/^@(\w+)\s*{/i);
      const type = typeMatch ? typeMatch[1].toLowerCase() : "unknown";

      // Extract ID (e.g., @article{uniqueID,)
      const idMatch = entry.match(/@\w+\s*{([^,]+),/i);
      const id = idMatch ? idMatch[1].trim() : `entry${index}`;

      // Extract ORCID (before colon in the ID)
      const orcid = id.includes(":") ? id.split(":")[0] : null;

      // Match fields, accounting for nested braces
      const fieldRegex = /(\w+)\s*=\s*({(?:[^{}]|{[^{}]*})*})/gs;
      const fields = {};
      let match;

      while ((match = fieldRegex.exec(entry)) !== null) {
        const key = match[1].toLowerCase().trim(); // Normalize field keys
        const value = match[2].replace(/^{|}$/g, "").trim(); // Remove outer braces and trim
        fields[key] = value;
      }

      // Normalize and parse specific fields
      const authors = fields.author
        ? fields.author.split(" and ").map((author) => author.trim())
        : [];

      const doi = fields.doi || "";
      const url = fields.url || "";

      // Skip entries without authors or both DOI and URL
      if (!authors.length || (!doi && !url)) {
        console.log(
          `Skipping entry with ID ${id} due to missing authors, DOI, or URL.`
        );
        return;
      }

      const publication = {
        id,
        orcid,
        type,
        authors,
        title: fields.title || "",
        journal: fields.journal || "",
        year: fields.year || "",
        month: fields.month || "",
        volume: fields.volume || "",
        doi,
        url,
        bibtex: entry.trim(), // Preserve original BibTeX entry
      };

      publications.push(publication);

      // Log each entry
      console.log(`Parsed Entry ${index + 1}:`, publication);
    } catch (error) {
      console.error(`Error parsing BibTeX entry at index ${index}:`, error);
    }
  });

  console.log("Parsed Publications:", publications);
  return publications;
}

function makeDropdownSearchable(dropdownId) {
  const selectElement = document.getElementById(dropdownId);

  // Preserve original options
  const originalOptions = Array.from(selectElement.options);

  // Hide the native dropdown and replace it with a custom one
  selectElement.style.display = "none";

  // Create a custom dropdown wrapper
  const wrapper = document.createElement("div");
  wrapper.style.position = "relative";
  wrapper.style.width = "100%";

  // Create a button to mimic the dropdown toggle
  const toggleButton = document.createElement("button");
  toggleButton.type = "button";
  toggleButton.className = "form-select";
  toggleButton.style.whiteSpace = "nowrap"; // Prevent text wrapping
  toggleButton.style.overflow = "hidden"; // Hide overflowed text
  toggleButton.style.textOverflow = "ellipsis"; // Show ellipsis for overflowed text
  toggleButton.textContent =
    selectElement.options[0]?.text || "Select an option";

  // Create the dropdown menu
  const dropdownMenu = document.createElement("div");
  dropdownMenu.style.display = "none";
  dropdownMenu.style.position = "absolute";
  dropdownMenu.style.width = "100%";
  dropdownMenu.style.border = "1px solid #ced4da";
  dropdownMenu.style.backgroundColor = "#fff";
  dropdownMenu.style.zIndex = "1000";
  dropdownMenu.style.maxHeight = "200px";
  dropdownMenu.style.overflowY = "auto";

  // Add a search input at the top of the dropdown menu
  const searchInput = document.createElement("input");
  searchInput.type = "text";
  searchInput.className = "form-control";
  searchInput.placeholder = "Type to search...";
  searchInput.style.margin = "0";
  searchInput.style.border = "none";
  searchInput.style.borderBottom = "1px solid #ced4da";
  dropdownMenu.appendChild(searchInput);

  // Add options to the dropdown menu
  const optionsContainer = document.createElement("div");
  dropdownMenu.appendChild(optionsContainer);

  // Populate the options container
  function populateOptions(query = "") {
    optionsContainer.innerHTML = ""; // Clear previous options
    originalOptions
      .filter((option) =>
        option.text.toLowerCase().includes(query.toLowerCase())
      )
      .forEach((option) => {
        const dropdownOption = document.createElement("div");
        dropdownOption.textContent = option.text;
        dropdownOption.style.padding = "8px";
        dropdownOption.style.cursor = "pointer";
        dropdownOption.style.whiteSpace = "normal"; // Allow full text during searches
        dropdownOption.addEventListener("click", () => {
          // Update the toggle button text and select the option
          toggleButton.textContent = option.text;
          toggleButton.title = option.text; // Add a tooltip with the full text
          selectElement.value = option.value;
          dropdownMenu.style.display = "none"; // Close the dropdown
          selectElement.dispatchEvent(new Event("change")); // Trigger change event
        });
        optionsContainer.appendChild(dropdownOption);
      });
  }

  populateOptions(); // Initialize with all options

  // Add search functionality
  searchInput.addEventListener("input", () => {
    populateOptions(searchInput.value);
  });

  // Toggle dropdown menu visibility
  toggleButton.addEventListener("click", () => {
    dropdownMenu.style.display =
      dropdownMenu.style.display === "none" ? "block" : "none";
    searchInput.focus();
  });

  // Close the dropdown when clicking outside
  document.addEventListener("click", (e) => {
    if (!wrapper.contains(e.target)) {
      dropdownMenu.style.display = "none";
    }
  });

  // Assemble the custom dropdown
  wrapper.appendChild(toggleButton);
  wrapper.appendChild(dropdownMenu);
  selectElement.parentElement.appendChild(wrapper);
}

// Populate dropdown filters
function populateFilters() {
  const authorSelect = document.getElementById("filterAuthor");
  const yearSelect = document.getElementById("filterYear");
  const journalSelect = document.getElementById("filterJournal");

  // Populate authors
  const sortedAuthors = Object.entries(authors).sort(([aName], [bName]) =>
    aName.localeCompare(bName)
  );
  sortedAuthors.forEach(([name, orcid]) => {
    const option = document.createElement("option");
    option.value = orcid;
    option.textContent = name;
    authorSelect.appendChild(option);
  });

  // Populate years
  const years = [...new Set(publications.map((pub) => pub.year))].sort();
  years.forEach((year) => {
    const option = document.createElement("option");
    option.value = year;
    option.textContent = year;
    yearSelect.appendChild(option);
  });

  // Populate journals
  const journals = [...new Set(publications.map((pub) => pub.journal))]
    .filter((j) => j)
    .sort();
  journals.forEach((journal) => {
    const option = document.createElement("option");
    option.value = journal;
    option.textContent = journal;
    journalSelect.appendChild(option);
  });

  populateItemsPerPage();
}

function populateItemsPerPage() {
  const itemsPerPageSelect = document.getElementById("itemsPerPage");
  if (!itemsPerPageSelect) {
    console.error("Dropdown for items per page not found.");
    return;
  }

  // Set a larger width for the dropdown
  itemsPerPageSelect.style.width = "115px"; // Adjust width as needed

  // Add default "Limit" option
  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = "Limit";
  defaultOption.disabled = true; // Make it non-selectable
  defaultOption.selected = true; // Set as the default selected option
  itemsPerPageSelect.appendChild(defaultOption);

  // Add other options
  [10, 20, 30, 40, 50, 60, 70, "All"].forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    itemsPerPageSelect.appendChild(option);
  });

  itemsPerPageSelect.addEventListener("change", (e) => {
    const selected = e.target.value;
    itemsPerPage =
      selected === "All" ? publications.length : parseInt(selected, 10);
    currentPage = 1;
    renderPublications();
  });
}

function renderPublications() {
  const search = document

    .getElementById("search")

    .value.toLowerCase()

    .trim();

  const authorOrcid = document.getElementById("filterAuthor").value; // Selected ORCID

  const year = document.getElementById("filterYear").value;

  const journal = document.getElementById("filterJournal").value;

  // Split the search query into individual words

  const searchWords = search.split(/\s+/).filter((word) => word); // Remove empty strings

  // Filter publications based on search and selected filters

  let filteredPublications = publications.filter((pub) => {
    // Multi-word prefix search across BibTeX entry

    const matchesSearch =
      !searchWords.length ||
      searchWords.every(
        (searchWord) =>
          pub.bibtex

            .toLowerCase()

            .split(/\s+/) // Split BibTeX into words

            .some((bibWord) => bibWord.startsWith(searchWord)) // Prefix match for each search word
      );

    const matchesAuthor = !authorOrcid || pub.orcid === authorOrcid;

    const matchesYear = !year || pub.year == year;

    const matchesJournal = !journal || pub.journal === journal;

    return matchesSearch && matchesAuthor && matchesYear && matchesJournal;
  });

  // Deduplicate results based on (title + DOI/URL) and (author + year)

  const seenPublications = new Set();

  filteredPublications = filteredPublications.filter((pub) => {
    const normalizedTitle = pub.title.toLowerCase().trim();

    const identifier = `${normalizedTitle}|${
      pub.doi || pub.url || ""
    }|${pub.authors.join(",").toLowerCase()}|${pub.year}`;

    if (seenPublications.has(identifier)) {
      return false; // Skip duplicates
    }

    seenPublications.add(identifier);
    return true; // Keep unique entries
  });

  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginated = filteredPublications.slice(
    startIndex,
    startIndex + itemsPerPage
  );

  const publicationList = document.getElementById("publicationList");

  publicationList.innerHTML = paginated

    .map(
      (pub) => `

<div class="card">

  <div class="card-body">

    <h5 class="card-title">${pub.title}</h5>

    <p class="card-text">Authors: ${pub.authors.join(", ")}, ${pub.year}</p>

    ${
      pub.doi || pub.url
        ? `<a href="${
            pub.doi ? `https://doi.org/${pub.doi}` : pub.url
          }" target="_blank" class="btn btn-primary">Read More</a>`
        : ""
    }

    <button class="btn btn-secondary" onclick="toggleBibTeX(this)">Show BibTeX</button>

    <div class="bibtex" style="display: none;">

        <pre>${pub.bibtex}</pre>

        <div id="bibtex-copied-message" class="mt-2" style="display: none;">Copied to clipboard!</div>

        <button class="btn btn-sm btn-outline-primary mt-2" onclick="copyBibTeX(this)">Copy BibTeX</button>

    </div>

  </div>

</div>

`
    )

    .join("");

  updateURLParams();

  renderPagination(filteredPublications.length);
}

function renderPagination(totalItems) {
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const pagination = document.querySelector(".pagination");
  pagination.innerHTML = "";

  // Add a wrapper for pagination numbers to allow multiline display
  const paginationWrapper = document.createElement("div");
  paginationWrapper.className =
    "pagination-wrapper d-flex flex-wrap justify-content-center";

  // Add "Previous" button
  const prevPage = document.createElement("li");
  prevPage.className = `page-item ${currentPage === 1 ? "disabled" : ""}`;
  prevPage.innerHTML = `<a class="page-link" href="#">Previous</a>`;
  prevPage.addEventListener("click", (e) => {
    e.preventDefault();
    if (currentPage > 1) {
      currentPage--;
      renderPublications();
    }
  });
  paginationWrapper.appendChild(prevPage);

  // Add page numbers dynamically
  for (let i = 1; i <= totalPages; i++) {
    const pageItem = document.createElement("li");
    pageItem.className = `page-item ${i === currentPage ? "active" : ""}`;
    pageItem.innerHTML = `<a class="page-link" href="#">${i}</a>`;
    pageItem.addEventListener("click", (e) => {
      e.preventDefault();
      currentPage = i;
      renderPublications();
    });
    paginationWrapper.appendChild(pageItem);
  }

  // Add "Next" button
  const nextPage = document.createElement("li");
  nextPage.className = `page-item ${
    currentPage === totalPages ? "disabled" : ""
  }`;
  nextPage.innerHTML = `<a class="page-link" href="#">Next</a>`;
  nextPage.addEventListener("click", (e) => {
    e.preventDefault();
    if (currentPage < totalPages) {
      currentPage++;
      renderPublications();
    }
  });
  paginationWrapper.appendChild(nextPage);

  pagination.appendChild(paginationWrapper);
}

// Set the current year in the copyright dynamically
function setCurrentYear() {
  const currentYear = new Date().getFullYear();
  document.getElementById("currentYear").textContent = currentYear;
}

// Call the function on page load
setCurrentYear();

function toggleBibTeX(button) {
  const bibtex = button.nextElementSibling;
  if (!bibtex.style.display || bibtex.style.display === "none") {
    bibtex.style.display = "block";
    button.textContent = "Hide BibTeX";
  } else {
    bibtex.style.display = "none";
    button.textContent = "Show BibTeX";
  }
}

function copyBibTeX(button) {
  const bibtexContent = button.previousElementSibling.textContent;
  navigator.clipboard.writeText(bibtexContent).then(() => {
    showMessage("BibTeX copied successfully!");
  });
}

// Function to display a non-intrusive message
function showMessage(message) {
  // Create the message container if it doesn't exist
  let messageContainer = document.getElementById("messageContainer");
  if (!messageContainer) {
    messageContainer = document.createElement("div");
    messageContainer.id = "messageContainer";
    messageContainer.style.position = "fixed";
    messageContainer.style.bottom = "20px";
    messageContainer.style.right = "20px";
    messageContainer.style.backgroundColor = "#007bff";
    messageContainer.style.color = "#fff";
    messageContainer.style.padding = "10px 15px";
    messageContainer.style.borderRadius = "5px";
    messageContainer.style.boxShadow = "0 2px 5px rgba(0, 0, 0, 0.2)";
    messageContainer.style.fontSize = "14px";
    messageContainer.style.zIndex = "1000";
    messageContainer.style.transition = "opacity 0.5s ease";
    document.body.appendChild(messageContainer);
  }

  // Set the message and show the container
  messageContainer.textContent = message;
  messageContainer.style.opacity = "1";

  // Hide the message after 3 seconds
  setTimeout(() => {
    messageContainer.style.opacity = "0";
    setTimeout(() => {
      if (messageContainer) {
        messageContainer.remove();
      }
    }, 500); // Delay for fade-out transition
  }, 3000);
}

function toggleTheme() {
  document.body.classList.toggle("dark-mode");
  const themeToggle = document.getElementById("themeToggle");
  themeToggle.textContent = document.body.classList.contains("dark-mode")
    ? "Switch to Light Mode"
    : "Switch to Dark Mode";
}

document.getElementById("themeToggle").addEventListener("click", toggleTheme);
document.getElementById("search").addEventListener("input", renderPublications);
document
  .getElementById("filterAuthor")
  .addEventListener("change", renderPublications);
document
  .getElementById("filterYear")
  .addEventListener("change", renderPublications);
document
  .getElementById("filterJournal")
  .addEventListener("change", renderPublications);

// loadData();

// Add event listeners to update URL and render publications
function addFilterListeners() {
  document
    .getElementById("search")
    .addEventListener("input", renderPublications);
  document
    .getElementById("filterAuthor")
    .addEventListener("change", renderPublications);
  document
    .getElementById("filterYear")
    .addEventListener("change", renderPublications);
  document
    .getElementById("filterJournal")
    .addEventListener("change", renderPublications);
}

document.addEventListener("DOMContentLoaded", () => {
  loadData();
  addFilterListeners();
});
