const searchInput = document.getElementById("searchInput");
const filterButtons = document.querySelectorAll(".filter-btn");
const cards = document.querySelectorAll(".product-card");
const totalProductos = document.getElementById("totalProductos");
const noResults = document.getElementById("noResults");
const menuToggle = document.getElementById("menuToggle");
const navLinks = document.getElementById("navLinks");
const requestedCategory = new URLSearchParams(window.location.search).get("categoria");
let activeFilter = ["electrónico", "libro"].includes(requestedCategory) ? requestedCategory : "todos";

const normalizeText = (value) => value.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();

function applyFilters() {
  const keyword = normalizeText(searchInput ? searchInput.value : "");
  let visible = 0;

  cards.forEach((card) => {
    const category = card.dataset.category;
    const searchText = normalizeText(card.dataset.search || "");
    const matchesCategory = activeFilter === "todos" || category === activeFilter;
    const matchesKeyword = !keyword || searchText.includes(keyword);
    const shouldShow = matchesCategory && matchesKeyword;
    card.classList.toggle("hidden", !shouldShow);
    if (shouldShow) visible += 1;
  });

  if (totalProductos) {
    totalProductos.textContent = `Mostrando ${visible} productos`;
  }
  if (noResults) {
    noResults.classList.toggle("hidden", visible > 0);
  }
}

if (searchInput) {
  searchInput.addEventListener("input", applyFilters);
}

filterButtons.forEach((button) => {
  const selected = button.dataset.filter === activeFilter;
  button.classList.toggle("active", selected);
  button.setAttribute("aria-pressed", String(selected));
  button.addEventListener("click", () => {
    filterButtons.forEach((item) => {
      const selected = item === button;
      item.classList.toggle("active", selected);
      item.setAttribute("aria-pressed", String(selected));
    });
    activeFilter = button.dataset.filter;
    applyFilters();
  });
});

document.querySelectorAll("[data-category-link]").forEach((link) => {
  link.addEventListener("click", (event) => {
    if (window.location.pathname === "/clientes") {
      event.preventDefault();
      activeFilter = link.dataset.categoryLink;
      filterButtons.forEach((button) => {
        const selected = button.dataset.filter === activeFilter;
        button.classList.toggle("active", selected);
        button.setAttribute("aria-pressed", String(selected));
      });
      applyFilters();
      document.getElementById("catalogo").scrollIntoView({ behavior: "smooth" });
      if (navLinks) {
        navLinks.classList.remove("open");
      }
      if (menuToggle) {
        menuToggle.setAttribute("aria-expanded", "false");
      }
    }
  });
});

if (menuToggle && navLinks) {
  menuToggle.addEventListener("click", () => {
    const expanded = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!expanded));
    menuToggle.setAttribute("aria-label", expanded ? "Abrir menú" : "Cerrar menú");
    navLinks.classList.toggle("open", !expanded);
  });

  navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      navLinks.classList.remove("open");
      menuToggle.setAttribute("aria-expanded", "false");
      menuToggle.setAttribute("aria-label", "Abrir menú");
    });
  });
}

const tipoSelect = document.getElementById("tipoProducto");
const campoGarantia = document.getElementById("campoGarantia");
const campoAutor = document.getElementById("campoAutor");
const campoTexto = document.getElementById("campoTexto");

if (tipoSelect && campoGarantia && campoAutor && campoTexto) {
  const toggleFormFields = () => {
    const isElectronico = tipoSelect.value === "electrónico";
    campoGarantia.classList.toggle("hidden", !isElectronico);
    campoAutor.classList.toggle("hidden", isElectronico);
    campoTexto.classList.toggle("hidden", isElectronico);
    campoGarantia.querySelector("input").required = isElectronico;
    campoAutor.querySelector("input").required = !isElectronico;
  };

  tipoSelect.addEventListener("change", toggleFormFields);
  toggleFormFields();
}

applyFilters();
